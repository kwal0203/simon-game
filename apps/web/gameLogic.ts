export type Phase = "idle" | "showing" | "input" | "won" | "lost";
export type Step = 0 | 1 | 2 | 3;
export type GameState = {
    phase: Phase;
    sequence: Step[];
    playerInput: Step[];
    strictMode: boolean;
};
export type Event =
    | { type: "START"; nextStep: Step }
    | { type: "SHOW_COMPLETE" }
    | { type: "INPUT"; step: Step }
    | { type: "RESET" };

export const initialState: GameState = {
    phase: "idle",
    sequence: [],
    playerInput: [],
    strictMode: false
};

export function transition(state: GameState, event: Event): GameState {
    switch (event.type) {
        case "START":
            if (state.phase !== "idle") return state;
            return { ...state, phase: "showing", sequence: [...state.sequence, event.nextStep], playerInput: [] };

        case "SHOW_COMPLETE":
            if (state.phase !== "showing") return state;
            return { ...state, phase: "input", playerInput: [] };

        case "INPUT":
            if (state.phase !== "input") return state;
            // Check if player input is correct
            const currentIndex = state.playerInput.length;
            const expected = state.sequence[currentIndex];

            if (event.step !== expected) {
                return state.strictMode
                    ? { ...state, phase: "lost", playerInput: [] }
                    : { ...state, phase: "showing", playerInput: [] }
            }

            const nextPlayerInput = [...state.playerInput, event.step];
            const roundComplete = nextPlayerInput.length === state.sequence.length;

            if (roundComplete) {
                return { ...state, phase: "showing", playerInput: [] };
            }

            return { ...state, playerInput: nextPlayerInput };

        case "RESET":
            return { phase: "idle", sequence: [], playerInput: [], strictMode: state.strictMode };

    }
}
