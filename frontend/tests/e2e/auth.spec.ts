import { expect, test, type Page } from '@playwright/test';

const ADMIN_IDENTIFIER =
  process.env.E2E_ADMIN_IDENTIFIER || 'ADM-0001';

const ADMIN_PASSWORD =
  process.env.E2E_ADMIN_PASSWORD || 'Admin@123';

async function fillIdentifier(page: Page, value: string) {
  const identifierInput = page.getByLabel(
    'Institutional Username / Identifier'
  );

  await identifierInput.click();
  await identifierInput.press('Control+A');
  await identifierInput.press('Backspace');
  await identifierInput.fill(value);
}

test.describe('authentication (real backend)', () => {
  test('valid admin login redirects to the protected dashboard', async ({
    page,
  }) => {
    await page.goto('/login');

    await fillIdentifier(page, ADMIN_IDENTIFIER);

    await page
      .getByLabel('Account Security Password')
      .fill(ADMIN_PASSWORD);

    await page
      .getByRole('button', {
        name: /authorize portal login/i,
      })
      .click();

    await expect(page).toHaveURL(/\/dashboard$/);

    await expect(
      page.getByRole('heading', {
        name: /institutional dashboard/i,
      })
    ).toBeVisible();
  });

  test('invalid credentials show an authentication error and stay on login', async ({
    page,
  }) => {
    await page.goto('/login');

    await fillIdentifier(page, 'ADM-999999');

    await page
      .getByLabel('Account Security Password')
      .fill('wrong-password');

    await page
      .getByRole('button', {
        name: /authorize portal login/i,
      })
      .click();

    await expect(
      page.getByText('Invalid identifier or password', {
        exact: true,
      })
    ).toBeVisible();

    await expect(page).toHaveURL(/\/login$/);
  });

  test('unauthenticated users are redirected away from a protected route', async ({
    page,
  }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveURL(
      /\/login\?redirect=%2Fdashboard/
    );

    await expect(
      page.getByRole('heading', {
        name: /institutional portal/i,
      })
    ).toBeVisible();
  });

  test('logout clears the session and protects the dashboard again', async ({
    page,
  }) => {
    await page.goto('/login');

    await fillIdentifier(page, ADMIN_IDENTIFIER);

    await page
      .getByLabel('Account Security Password')
      .fill(ADMIN_PASSWORD);

    await page
      .getByRole('button', {
        name: /authorize portal login/i,
      })
      .click();

    await expect(page).toHaveURL(/\/dashboard$/);

    await page
      .getByRole('button', {
        name: /sign out/i,
      })
      .click();

    await expect(page).toHaveURL(
      /\/login\?redirect=%2Fdashboard/
    );

    await page.goto('/dashboard');

    await expect(page).toHaveURL(
      /\/login\?redirect=%2Fdashboard/
    );
  });

  test('authenticated session loads the protected shell', async ({
    page,
  }) => {
    await page.goto('/login');

    await fillIdentifier(page, ADMIN_IDENTIFIER);

    await page
      .getByLabel('Account Security Password')
      .fill(ADMIN_PASSWORD);

    await page
      .getByRole('button', {
        name: /authorize portal login/i,
      })
      .click();

    await expect(page).toHaveURL(/\/dashboard$/);

    await expect(
      page.getByRole('navigation', {
        name: /portal navigation/i,
      })
    ).toBeVisible();

    await expect(
      page.getByRole('button', {
        name: /sign out/i,
      })
    ).toBeVisible();
  });
});