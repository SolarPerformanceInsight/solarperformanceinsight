// Copyright (c) 2020 RisingStack
export class User {
  sub!: string;
  names!: string;
  nickname!: string;
  picture!: string;
  updated_at!: string;
  email!: string;
  email_verified!: boolean;

  provider?: string;
  id?: string;

  given_name?: string;
  family_name?: string;
  locale?: string;
  [key: string]: string | boolean | undefined;

  constructor(auth0User: { [key: string]: string | boolean | undefined }) {
    if (!auth0User) return;
    for (const key in auth0User) {
      this[key] = auth0User[key];
    }

    this.sub = auth0User.sub as string;
    this.provider = this.sub.split("|")[0];
    this.id = this.sub.split("|")[1];
  }
}
