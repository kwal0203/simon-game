import { describe, it, expect } from "vitest";
import { nextSequence } from "../gameLogic";

describe("nextSequence", () => {
    it("Increases sequence length by 1", () => {
        const before = [0, 2, 1];
        const after = nextSequence(before, 3);

        expect(after).toHaveLength(before.length + 1);
        expect(after).toEqual([0, 2, 1, 3]);
    });
});
