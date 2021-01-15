import jwt_decode from 'jwt-decode';

//declare global {
//  // eslint-disable-next-line @typescript-eslint/no-namespace
//  namespace Cypress {
//    interface Chainable<Subject> {
//      login(username: string, password: string): Chainable<Subject>;
//    }
//  }
//}

Cypress.Commands.add('login', (username: string, password: string) => {
  cy.log(`Logging in as ${username}`);
  const client_id = Cypress.env('auth_client_id');
  const client_secret = Cypress.env('auth_client_secret');
  const audience = Cypress.env('auth_audience');
  const scope = 'openid profile email offline_access';

  const options = {
    method: 'POST',
    url: Cypress.env('auth_url'),
    body: {
      grant_type: 'password',
      username,
      password,
      audience,
      scope,
      client_id,
      client_secret,
    },
  };
  cy.request(options).then(({ body }) => {
    const { access_token, expires_in, id_token } = body;
    const key = `@@auth0spajs@@::${client_id}::${audience}::${scope}`;
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
});
