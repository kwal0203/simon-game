import { useReducer } from "react";
import { transition, initialState } from "./gameLogic";

export default function SimonGame() {
    const [state, dispatch] = useReducer(transition, initialState);

    const onStart = () => dispatch({ type: "START", nextStep: 2 });
    // const onShowComplete = () => dispatch({ type: "SHOW_COMPLETE" });
    const onPadClick = (step: 0 | 1 | 2 | 3) => dispatch({ type: "INPUT", step });
    const onReset = () => dispatch({ type: "RESET" });

    return (
        <div>
            <button onClick={onStart}>Start</button>
            <button onClick={() => onPadClick(0)}>Pad 0</button>
            <button onClick={onReset}>Reset</button>
        </div>
    )
}
