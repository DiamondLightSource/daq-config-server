import { screen } from "@testing-library/react";
import { App } from "./App";
import { render } from "./test-utils";

test("title is displayed", () => {
  render(<App />);
  const titleText = screen.getByText(/Read and store configuration for I03 Hyperion/i);
  expect(titleText).toBeInTheDocument();
});
