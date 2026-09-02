import { expect, test } from '@playwright/test';

/**
 * These tests exercise the REAL backend auth flow (POST /auth/login,
 * GET /auth/me, POST /auth/logout via the httpOnly access_token cookie),
 * not a frontend fake. They require:
 *
 *  1. The FastAPI backend running and reachable at BACKEND_API_URL
 *     (see next.config.ts / .env.local.example).
 *  2. A seeded account to log in with. Defaults below match what the
 *     backend's own create_admin.py seeds (admin@example.com), but can be
 *     overridden with E2E_ADMIN_EMAIL / E2E_ADMIN_PASSWORD for any other
 *     environment/test database.
 */
const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@example.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'Admin@123';

test.describe('authentication (real backend)', () => {
  test('valid login redirects to the protected dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(ADMIN_EMAIL);
    await page.getByLabel('Password').fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole('heading', { name: /Welcome/ })).toBeVisible();
  });

  test('invalid credentials show an authentication error and stay on /login', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('wrong@example.com');
    await page.getByLabel('Password').fill('wrong-password');
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page.getByRole('main').getByRole('alert')).toContainText('Invalid email or password.');
    await expect(page).toHaveURL(/\/login$/);
  });

  test('unauthenticated users are redirected away from a protected route', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveURL(/\/login\?redirect=%2Fdashboard/);
    await expect(page.getByText('Please sign in to continue.')).toBeVisible();
  });

  test('logout clears the session and returns to a protected-route redirect', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(ADMIN_EMAIL);
    await page.getByLabel('Password').fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL(/\/dashboard$/);

    await page.getByRole('button', { name: 'Sign out' }).click();
    await expect(page).toHaveURL(/\/login$/);

    // The session cookie is gone server-side - protected routes bounce again.
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login\?redirect=%2Fdashboard/);
  });

  test('authenticated session loads the protected shell (sidebar + header)', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(ADMIN_EMAIL);
    await page.getByLabel('Password').fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole('navigation', { name: 'Primary' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
  });
});
