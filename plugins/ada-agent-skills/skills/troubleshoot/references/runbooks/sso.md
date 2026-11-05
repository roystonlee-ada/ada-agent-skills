# SSO setup and changes

Use when the person wants single sign-on for the Ada dashboard, or wants to
change the identity provider.

## Preconditions

- An Ada representative takes part. Setup is not self-serve.
- The identity provider supports SAML 2.0.
- Another Owner or Admin keeps a password login until SSO works. Record the
  current user list and roles first.

## Steps

1. Ask the Ada representative to start SSO setup. Ada gives the ACS URL and
   the Audience URI.
2. Send Ada the identity provider's entity ID, Single Sign-On URL and
   signing certificate.
3. Set the Name ID format to email, with the attributes email, firstName and
   lastName.
4. Users on a password login must be deleted and added again in Ada with the
   login type SSO. A user has one login method only. There is no login
   starting from the identity provider.
5. The same identity provider works for several Ada instances. Each instance
   needs its own user adds.

SSO and MFA accounts sign in to adacli by device login.

## Downtime risk

Users who are removed and re-added cannot sign in between the two steps. Do
the swap for one Owner first and confirm sign-in before the rest. Keep one
password-based Owner until every SSO login is confirmed.

## How to verify

Sign in as a re-added user through the identity provider. Check the audit
log for the SSO configuration entry.

## Rollback

Ask the Ada representative to disable SSO, then re-add users with a password
login. Use the user list recorded first.

## Source

- `product-docs/fern/versions/pages/docs/other/team-access/sso.mdx`
- `.../team-access/my-team.mdx`
- `adacli/docs/guide.md` (device login for SSO accounts)

## OPEN or ASSUMED

- OPEN: how long the Ada side of setup takes.
- OPEN: how to move to a new identity provider. The docs cover first setup
  only. Ask the representative.
