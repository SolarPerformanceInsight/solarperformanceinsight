describe("Test Dash", () => {
  it("Connect to home", () => {
    cy.visit("http://localhost:8001");

    cy.contains("Welcome to the solarperformance");
  });
});
