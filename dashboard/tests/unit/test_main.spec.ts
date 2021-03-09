import "./mockauth";
import "./mockvalidator";

describe("Test main by hitting home", () => {
  it("home", async () => {
    document.body.innerHTML = '<div id="app"></div>';
    require("../../src/main");
    const unauthHome = document.querySelector(".unauth-home");
    expect(unauthHome).toBeTruthy();
    // @ts-expect-error
    expect(unauthHome.textContent.trim()).toEqual(
      `Welcome to the solarperformance insight dashboard. Other information
      about the project.`
    );
  });
});
