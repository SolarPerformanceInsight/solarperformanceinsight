import jwt_decode from 'jwt-decode';

Cypress.Commands.add('login', (username: string, password: string) => {
  cy.log(`Logging in as ${username}`);
  const client_id = Cypress.env('AUTH_CLIENT_ID');
  const client_secret = Cypress.env('AUTH_CLIENT_SECRET');
  const audience = Cypress.env('AUTH_AUDIENCE');
  const scope = 'openid profile email offline_access';

  // Hardcode localStorage key. We can retrireve a token from the test application
  // and place it in localStorage with the dev apps id.
  const key = `@@auth0spajs@@::H93iiI1JcKgL5lFfRBD2XGdboHzzgUQf::https://app.solarperformanceinsight.org/api::openid profile email offline_access`;
  if (localStorage.getItem(key) === null) {
    const options = {
      method: 'POST',
      url: Cypress.env('AUTH_URL'),
      body: {
        grant_type: 'password',
        username,
        password,
        audience,
        scope,
        client_id,
      },
    };
    cy.request(options).then(({ body }) => {
      const { access_token, expires_in, id_token } = body;
      const auth0Cache = {
        body: {
          client_id,
          access_token,
          id_token,
          scope,
          expires_in,
          decodedToken: {
            user: jwt_decode(id_token),
          },
        },
        expiresAt: Math.floor(Date.now() / 1000) + expires_in,
      };
      window.localStorage.setItem(key, JSON.stringify(auth0Cache));
    });
  }
});
