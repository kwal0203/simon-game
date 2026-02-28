import { describe, it, expect } from "vitest";
import { transition, initialState, type GameState } from "../gameLogic";
import { StrictMode } from "react";

describe("transition", () => {
    it("START appends a step and moves to showing", () => {
        const next = transition(initialState, { type: "START", nextStep: 2 });

        expect(next.sequence).toEqual([2]);
        expect(next.phase).toBe("showing");
        expect(next.playerInput).toEqual([]);
    });

    it("SHOW_COMPLETE moves from showing to input", () => {
        const started = transition(initialState, { type: "START", nextStep: 1 });
        const next = transition(started, { type: "SHOW_COMPLETE" });

        expect(next.phase).toBe("input");
        expect(next.sequence).toEqual([1]);
    });

    it("correct INPUT appends player input while round is in progress", () => {
        const state: GameState = {
            ...initialState,
            phase: "input",
            sequence: [0, 2],
            playerInput: [],
        };

        const next = transition(state, { type: "INPUT", step: 0 });

        expect(next.phase).toBe("input");
        expect(next.playerInput).toEqual([0]);
    });

    it("wrong INPUT in strict mode loses the game", () => {
        const state: GameState = {
            ...initialState,
            phase: "input",
            strictMode: true,
            sequence: [1],
            playerInput: []
        };

        const next = transition(state, { type: "INPUT", step: 0 });

        expect(next.phase).toBe("lost");
        expect(next.playerInput).toEqual([]);
    });

    it("wrong INPUT in non-strict mode replays round", () => {
        const state: GameState = {
            ...initialState,
            phase: "input",
            strictMode: false,
            sequence: [3],
            playerInput: [],
        };

        const next = transition(state, { type: "INPUT", step: 0 });

        expect(next.phase).toBe("showing");
        expect(next.playerInput).toEqual([]);
    });

    it("RESET returns to idle and preserves strict mode setting", () => {
        const state: GameState = {
            ...initialState,
            phase: "input",
            strictMode: true,
            sequence: [0, 1],
            playerInput: [0],
        };

        const next = transition(state, { type: "RESET" });

        expect(next).toEqual({
            phase: "idle",
            sequence: [],
            playerInput: [],
            strictMode: true,
        });
    });
});
