import { useEffect, useMemo, useRef, useState } from "react";
import { transition, initialState } from "./gameLogic";
import type { Step } from "./gameLogic";
import "./SimonGame.css";

type LeaderboardRow = {
    score: number;
    rank: number;
    display_name: string;
};

type LeaderboardResponse = {
    scores: LeaderboardRow[];
};

type SubmitScoreResponse = {
    score_id: string;
    rank: number;
};

const PAD_META: Record<Step, { label: string; className: string; frequency: number }> = {
    0: { label: "Green", className: "pad-green", frequency: 261.63 },
    1: { label: "Red", className: "pad-red", frequency: 329.63 },
    2: { label: "Yellow", className: "pad-yellow", frequency: 392.0 },
    3: { label: "Blue", className: "pad-blue", frequency: 523.25 },
};

const PAD_STEPS: Step[] = [0, 1, 2, 3];

function randomStep(): Step {
    return Math.floor(Math.random() * 4) as Step;
}

function getCookie(name: string): string | null {
    const target = `${name}=`;
    const parts = document.cookie.split(";").map((item) => item.trim());
    const match = parts.find((part) => part.startsWith(target));
    return match ? decodeURIComponent(match.slice(target.length)) : null;
}

function setCookie(name: string, value: string, maxAgeSeconds: number): void {
    document.cookie = `${name}=${encodeURIComponent(value)}; Path=/; Max-Age=${maxAgeSeconds}; SameSite=Lax`;
}

function getOrCreatePlayerId(): string {
    const existing = getCookie("player_id");
    if (existing) return existing;
    const created = crypto.randomUUID();
    setCookie("player_id", created, 60 * 60 * 24 * 365);
    return created;
}

export default function SimonGame() {
    const [state, setState] = useState(initialState);
    const [activeStep, setActiveStep] = useState<Step | null>(null);
    const [displayName, setDisplayName] = useState("");
    const [isGameOver, setIsGameOver] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLoadingLeaderboard, setIsLoadingLeaderboard] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [submissionRank, setSubmissionRank] = useState<number | null>(null);
    const [finalScore, setFinalScore] = useState<number | null>(null);
    const [leaderboard, setLeaderboard] = useState<LeaderboardRow[]>([]);
    const [submittedScoreId, setSubmittedScoreId] = useState<string | null>(null);
    const [isAdvancingRound, setIsAdvancingRound] = useState(false);
    const idempotencyKeyRef = useRef<string>("");
    const audioContextRef = useRef<AudioContext | null>(null);
    const sequenceTimeoutsRef = useRef<number[]>([]);
    const roundAdvanceTimeoutRef = useRef<number | null>(null);
    const playerId = useMemo(() => getOrCreatePlayerId(), []);
    const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").toString();

    const currentScore = Math.max(0, state.sequence.length - 1);
    const canStart = state.phase === "idle" && displayName.trim().length > 0;

    function updateState(event: Parameters<typeof transition>[1]): void {
        setState((prev) => transition(prev, event));
    }

    function clearScheduledPlayback(): void {
        for (const timeoutId of sequenceTimeoutsRef.current) {
            window.clearTimeout(timeoutId);
        }
        sequenceTimeoutsRef.current = [];
        if (roundAdvanceTimeoutRef.current !== null) {
            window.clearTimeout(roundAdvanceTimeoutRef.current);
            roundAdvanceTimeoutRef.current = null;
        }
    }

    function playTone(step: Step): void {
        const AudioCtx = window.AudioContext || (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
        if (!AudioCtx) return;
        if (!audioContextRef.current) {
            audioContextRef.current = new AudioCtx();
        }
        const context = audioContextRef.current;
        const oscillator = context.createOscillator();
        const gain = context.createGain();
        oscillator.type = "sine";
        oscillator.frequency.value = PAD_META[step].frequency;
        gain.gain.setValueAtTime(0.0001, context.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.16, context.currentTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.23);
        oscillator.connect(gain);
        gain.connect(context.destination);
        oscillator.start();
        oscillator.stop(context.currentTime + 0.24);
    }

    function fetchLeaderboard(): Promise<void> {
        setIsLoadingLeaderboard(true);
        return fetch(`${apiBaseUrl}/v1/leaderboard`, {
            credentials: "include",
            method: "GET",
        })
            .then(async (response) => {
                if (!response.ok) {
                    throw new Error(`Leaderboard request failed (${response.status})`);
                }
                const body = (await response.json()) as LeaderboardResponse;
                setLeaderboard(body.scores ?? []);
            })
            .catch((error: unknown) => {
                setErrorMessage(
                    error instanceof Error
                        ? error.message
                        : "Unable to load leaderboard.",
                );
            })
            .finally(() => {
                setIsLoadingLeaderboard(false);
            });
    }

    async function submitScore(score: number): Promise<void> {
        if (!idempotencyKeyRef.current) {
            idempotencyKeyRef.current = crypto.randomUUID();
        }
        setIsSubmitting(true);
        try {
            const response = await fetch(`${apiBaseUrl}/v1/scores`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "content-type": "application/json",
                    "idempotency-key": idempotencyKeyRef.current,
                },
                body: JSON.stringify({ score, display_name: displayName.trim() }),
            });
            if (!response.ok) {
                throw new Error(`Score submission failed (${response.status})`);
            }
            const body = (await response.json()) as SubmitScoreResponse;
            setSubmissionRank(body.rank);
            setSubmittedScoreId(body.score_id);
        } catch (error: unknown) {
            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "Unable to submit score.",
            );
        } finally {
            setIsSubmitting(false);
        }
    }

    function endGameAndLoadResults(score: number): void {
        setIsGameOver(true);
        setFinalScore(score);
        void submitScore(score).finally(() => {
            void fetchLeaderboard();
        });
    }

    function onStart(): void {
        setErrorMessage(null);
        setLeaderboard([]);
        setSubmissionRank(null);
        setSubmittedScoreId(null);
        setFinalScore(null);
        setIsGameOver(false);
        idempotencyKeyRef.current = crypto.randomUUID();
        setCookie("player_id", playerId, 60 * 60 * 24 * 365);
        updateState({ type: "RESET" });
        updateState({ type: "START", nextStep: randomStep() });
    }

    function onPadClick(step: Step): void {
        if (state.phase !== "input" || isGameOver) return;
        setActiveStep(step);
        playTone(step);
        window.setTimeout(() => setActiveStep(null), 160);

        const currentIndex = state.playerInput.length;
        const expectedStep = state.sequence[currentIndex];
        const isCorrect = step === expectedStep;
        const isRoundComplete = isCorrect && currentIndex === state.sequence.length - 1;
        updateState({ type: "INPUT", step });

        if (!isCorrect) {
            endGameAndLoadResults(currentScore);
            return;
        }

        if (isRoundComplete) {
            setIsAdvancingRound(true);
            roundAdvanceTimeoutRef.current = window.setTimeout(() => {
                updateState({ type: "NEXT_ROUND", nextStep: randomStep() });
                setIsAdvancingRound(false);
                roundAdvanceTimeoutRef.current = null;
            }, 1000);
        }
    }

    function onReset(): void {
        clearScheduledPlayback();
        setActiveStep(null);
        setErrorMessage(null);
        setLeaderboard([]);
        setSubmissionRank(null);
        setFinalScore(null);
        setSubmittedScoreId(null);
        setIsGameOver(false);
        setIsAdvancingRound(false);
        updateState({ type: "RESET" });
    }

    useEffect(() => {
        if (state.phase !== "showing" || isGameOver || isAdvancingRound) return;
        clearScheduledPlayback();
        setActiveStep(null);

        let currentDelay = 250;
        for (const step of state.sequence) {
            const onTimeout = window.setTimeout(() => {
                setActiveStep(step);
                playTone(step);
            }, currentDelay);
            sequenceTimeoutsRef.current.push(onTimeout);

            const offTimeout = window.setTimeout(() => {
                setActiveStep(null);
            }, currentDelay + 350);
            sequenceTimeoutsRef.current.push(offTimeout);

            currentDelay += 500;
        }

        const doneTimeout = window.setTimeout(() => {
            setActiveStep(null);
            updateState({ type: "SHOW_COMPLETE" });
        }, currentDelay);
        sequenceTimeoutsRef.current.push(doneTimeout);

        return () => {
            clearScheduledPlayback();
        };
    }, [state.phase, state.sequence, isGameOver, isAdvancingRound]);

    useEffect(() => {
        return () => {
            clearScheduledPlayback();
            audioContextRef.current?.close();
        };
    }, []);

    const leaderboardRows = (() => {
        const rows = [...leaderboard];
        if (
            submissionRank !== null &&
            finalScore !== null &&
            !rows.some((row) => row.rank === submissionRank)
        ) {
            rows.push({
                rank: submissionRank,
                score: finalScore,
                display_name: displayName.trim() || "You",
            });
        }
        return rows;
    })();

    return (
        <main className="simon-page">
            <section className="game-card">
                <h1>Simon Game</h1>
                <p className="subhead">Repeat the pattern. One mistake ends the run.</p>
                <div className="status-grid">
                    <div>
                        <span>Phase</span>
                        <strong>{state.phase}</strong>
                    </div>
                    <div>
                        <span>Round</span>
                        <strong>{state.sequence.length}</strong>
                    </div>
                    <div>
                        <span>Score</span>
                        <strong>{currentScore}</strong>
                    </div>
                </div>

                <label className="name-row">
                    <span>Display name</span>
                    <input
                        value={displayName}
                        onChange={(event) => setDisplayName(event.target.value)}
                        maxLength={16}
                        placeholder="Enter name"
                    />
                </label>

                <div className="controls">
                    <button onClick={onStart} disabled={!canStart}>
                        Start Game
                    </button>
                    <button onClick={onReset}>
                        Reset
                    </button>
                </div>

                <div className="pad-grid" aria-label="Simon pads">
                    {PAD_STEPS.map((step) => (
                        <button
                            key={step}
                            className={`pad ${PAD_META[step].className} ${activeStep === step ? "active" : ""}`}
                            onClick={() => onPadClick(step)}
                            disabled={state.phase !== "input" || isGameOver}
                            aria-label={PAD_META[step].label}
                        >
                            {PAD_META[step].label}
                        </button>
                    ))}
                </div>

                {errorMessage ? <p className="error">{errorMessage}</p> : null}
                {submittedScoreId ? <p className="hint">Submission id: {submittedScoreId}</p> : null}
            </section>

            <section className="leaderboard-card">
                <div className="leaderboard-head">
                    <h2>Leaderboard</h2>
                    {isGameOver ? <span className="pill">Game Over</span> : <span className="pill muted">In Progress</span>}
                </div>
                {isSubmitting ? <p>Submitting score...</p> : null}
                {isLoadingLeaderboard ? <p>Loading leaderboard...</p> : null}
                {!isGameOver ? <p className="hint">Leaderboard appears when the run ends.</p> : null}
                {isGameOver && finalScore !== null ? <p className="hint">Final score: {finalScore}</p> : null}
                {submissionRank !== null ? <p className="hint">Your rank: {submissionRank}</p> : null}

                {leaderboardRows.length > 0 ? (
                    <ol className="leaderboard-list">
                        {leaderboardRows.slice(0, 101).map((row) => {
                            const isCurrentUser = submissionRank !== null && row.rank === submissionRank;
                            return (
                                <li key={`${row.rank}-${row.display_name}-${row.score}`} className={isCurrentUser ? "mine" : ""}>
                                    <span>#{row.rank}</span>
                                    <span>{row.display_name}</span>
                                    <strong>{row.score}</strong>
                                </li>
                            );
                        })}
                    </ol>
                ) : null}
            </section>
        </main>
    );
}
