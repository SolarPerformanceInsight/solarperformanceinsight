import * as auth from "@/auth/auth";

const mockedAuthInstance = jest.spyOn(auth, "getInstance");

const user = {
 email: "testing@solaforecastarbiter.org",
 email_verified: true,
 sub: "auth0|5fa9596ccf64f9006e841a3a"
};

const $auth = {
 isAuthenticated: true,
 loading: false,
 user: user,
 logout: jest.fn(),
 loginWithRedirect: jest.fn(),
 getTokenSilently: jest.fn().mockReturnValue("Token")
};

// @ts-expect-error
mockedAuthInstance.mockImplementation(() => $auth);

export { mockedAuthInstance, $auth };
