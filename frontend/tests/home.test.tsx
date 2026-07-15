import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders the platform title", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "ApexFlow AI" })).toBeInTheDocument();
  });
});
