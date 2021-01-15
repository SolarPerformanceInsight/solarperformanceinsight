describe("Test Dash", () => {
  it("Connect to home", () => {
    cy.visit("http://localhost:8001");

    cy.contains("Welcome to the solarperformance");
  });
  it("Connect to systems", () => {
    cy.login(Cypress.env("auth_username"), Cypress.env("auth_password"));

    cy.visit("http://localhost:8001/systems");

    cy.get("h1").contains("Systems");
  });
  it("Connect to new System", () => {
    cy.login(Cypress.env("auth_username"), Cypress.env("auth_password"));

    cy.visit("http://localhost:8001/systems/new");

    cy.get("h1").contains("New System");
  });
});
