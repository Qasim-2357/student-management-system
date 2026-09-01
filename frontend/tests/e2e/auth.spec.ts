import { expect, test } from '@playwright/test';

const validEmail = 'admin@example.com';
const validPassword = 'password123';

test.describe('authentication smoke tests', () => {
  test('valid login redirects to the dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(validEmail);
    await page.getByLabel('Password').fill(validPassword);
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByText(`Welcome back, ${validEmail}`)).toBeVisible();
  });

  test('invalid login shows an authentication error', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('wrong@example.com');
    await page.getByLabel('Password').fill('wrong-password');
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page.getByText('Invalid email or password.')).toBeVisible();
  });

  test('unauthenticated users are redirected away from the dashboard', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveURL(/\/login\?/);
    await expect(page.getByText('Please sign in to continue.')).toBeVisible();
  });

  test('logout clears the session and returns to login', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(validEmail);
    await page.getByLabel('Password').fill(validPassword);
    await page.getByRole('button', { name: 'Sign in' }).click();

    await page.getByRole('button', { name: 'Log out' }).click();

    await expect(page).toHaveURL(/\/login$/);
    const rawSession = await page.evaluate(() => localStorage.getItem('session'));
    expect(rawSession).toBeNull();
  });

  test('authenticated session loads the dashboard correctly', async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem(
        'session',
        JSON.stringify({ user: { email: 'admin@example.com', role: 'admin' } }),
      );
    });

    await page.goto('/dashboard');

    await expect(page.getByText('Dashboard')).toBeVisible();
    await expect(page.getByText('Welcome back, admin@example.com')).toBeVisible();
  });
});
