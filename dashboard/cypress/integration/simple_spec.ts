describe("Test Dash", () => {
  it("Connect to home", () => {
    cy.visit("http://localhost:8001");

    cy.contains("Welcome to the solarperformance");
  });
  it("Connect to systems", () => {
    cy.login(Cypress.env("AUTH_USERNAME"), Cypress.env("AUTH_PASSWORD"));

    cy.visit("http://localhost:8001");

    cy.contains("Successfully logged in.");
  });
  it("Connect to new System", () => {
    cy.login(Cypress.env("AUTH_USERNAME"), Cypress.env("AUTH_PASSWORD"));

    cy.visit("http://localhost:8001/system/new");

    cy.get("h1").contains("New System");
  });
});
