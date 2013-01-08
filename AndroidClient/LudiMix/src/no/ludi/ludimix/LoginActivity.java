package no.ludi.ludimix;

import android.annotation.TargetApi;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.NavUtils;
import android.text.TextUtils;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.TextView;

/**
 * Activity which displays a login screen to the user, offering registration as
 * well.
 */
public class LoginActivity extends Activity {

	/**
	 * Keep track of the login task to ensure we can cancel it if requested.
	 */
	private UserLoginTask mAuthTask = null;
	
	public static final String RESULT_EXTRA_STATUS = "0";
	public static final String SETTINGS_USER_ONLINE = "user_online";
	public static final String SETTINGS_USER_MAIL = "user_mail";
	public static final String SETTINGS_USER_ID = "user_id";
	public static final String SETTINGS_USER_SECURE_TOKEN = "user_secure_token";
	
	private static enum State { OFFLINE, ONLINE, LOGGING_IN };
	
	// Values for email and password at the time of the login attempt.
	private String mEmail;
	private String mPassword;
	private String mToken;
	private int mUserId;

	// Info UI references.
	private TextView iUserId;
	private TextView iEmail;
	
	// UI references.
	private EditText mEmailView;
	private EditText mPasswordView;
	private View mLoginFormView;
	private View mLoginStatusView;
	private View mLoginInfoView;
	private TextView mLoginStatusMessageView;
	
	// Settings
	SharedPreferences settings;

	private MenuItem logout_button;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		setContentView(R.layout.activity_login);
		setupActionBar();

		// Set up the login form.
		settings = getSharedPreferences("login_data", 0);
		
		iEmail = (TextView) findViewById(R.id.iEmail);
		iUserId = (TextView) findViewById(R.id.iUserId);
		
		mEmail = settings.getString(SETTINGS_USER_MAIL, "");
		mEmailView = (EditText) findViewById(R.id.email);
		mEmailView.setText(mEmail);
		
		mPasswordView = (EditText) findViewById(R.id.password);
		mPasswordView
				.setOnEditorActionListener(new TextView.OnEditorActionListener() {
					@Override
					public boolean onEditorAction(TextView textView, int id, KeyEvent keyEvent) {
						if (id == R.id.login || id == EditorInfo.IME_NULL) {
							attemptLogin();
							return true;
						}
						return false;
					}
				});

		mLoginFormView = findViewById(R.id.login_form);
		mLoginStatusView = findViewById(R.id.login_status);
		mLoginInfoView = findViewById(R.id.login_info);
		mLoginStatusMessageView = (TextView) findViewById(R.id.login_status_message);

		findViewById(R.id.sign_in_button).setOnClickListener(
				new View.OnClickListener() {
					@Override
					public void onClick(View view) {
						attemptLogin();
					}
				});
		
		boolean gotLoginData = settings.getBoolean(SETTINGS_USER_ONLINE, false);
		if (gotLoginData) {
			updateViews(State.ONLINE);
		}
		else {
			updateViews(State.OFFLINE);
		}

	}

	/**
	 * Set up the {@link android.app.ActionBar}, if the API is available.
	 */
	@TargetApi(Build.VERSION_CODES.HONEYCOMB)
	private void setupActionBar() {
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
			// Show the Up button in the action bar.
			getActionBar().setDisplayHomeAsUpEnabled(true);
		}
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		switch (item.getItemId()) {
		case android.R.id.home:
			NavUtils.navigateUpFromSameTask(this);
			return true;
		case R.id.menu_logout:
			handleLoggedOut(true);
			return true;
		}
		return super.onOptionsItemSelected(item);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		super.onCreateOptionsMenu(menu);
		boolean user_online = settings.getBoolean(SETTINGS_USER_ONLINE, false);
		getMenuInflater().inflate(R.menu.activity_login, menu);
		this.logout_button = menu.getItem(0);
		if (!user_online) {
			logout_button.setVisible(false);
		}
		
		return true;
	}

	/**
	 * Attempts to sign in or register the account specified by the login form.
	 * If there are form errors (invalid email, missing fields, etc.), the
	 * errors are presented and no actual login attempt is made.
	 */
	public void attemptLogin() {
		if (mAuthTask != null) {
			return;
		}

		// Reset errors.
		mEmailView.setError(null);
		mPasswordView.setError(null);

		// Store values at the time of the login attempt.
		mEmail = mEmailView.getText().toString();
		mPassword = mPasswordView.getText().toString();
		mUserId = 0;

		boolean cancel = false;
		View focusView = null;

		// Check for a valid password.
		if (TextUtils.isEmpty(mPassword)) {
			mPasswordView.setError(getString(R.string.error_field_required));
			focusView = mPasswordView;
			cancel = true;
		} else if (mPassword.length() < 8) {
			mPasswordView.setError(getString(R.string.error_invalid_password));
			mPasswordView.setText("");
			focusView = mPasswordView;
			cancel = true;
		}

		// Check for a valid email address.
		if (TextUtils.isEmpty(mEmail)) {
			mEmailView.setError(getString(R.string.error_field_required));
			focusView = mEmailView;
			cancel = true;
		} else if (!mEmail.contains("@")) {
			mEmailView.setError(getString(R.string.error_invalid_email));
			focusView = mEmailView;
			cancel = true;
		}

		if (cancel) {
			// There was an error; don't attempt login and focus the first
			// form field with an error.
			//focusView.requestFocus();
		} else {
			// Show a progress spinner, and kick off a background task to
			// perform the user login attempt.
			mLoginStatusMessageView.setText(R.string.login_progress_signing_in);
			updateViews(State.LOGGING_IN);
			mAuthTask = new UserLoginTask();
			mAuthTask.execute((Void) null);
		}
	}

	/**
	 * Shows the progress UI and hides the login form.
	 */
	@TargetApi(Build.VERSION_CODES.HONEYCOMB_MR2)
	private void updateViews(final State state) {
		final boolean showOffline = (state == State.OFFLINE);
		final boolean showOnline = (state == State.ONLINE);
		final boolean showLoggingIn = (state == State.LOGGING_IN);

		if (showOnline) {
			iEmail.setText("email: " + settings.getString(SETTINGS_USER_MAIL, "user@example.com"));
			iUserId.setText("UserID: " + settings.getInt(SETTINGS_USER_ID, 0));
		}

//		// On Honeycomb MR2 we have the ViewPropertyAnimator APIs, which allow
//		// for very easy animations. If available, use these APIs to fade-in
//		// the progress spinner.
//		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB_MR2) {
//			int shortAnimTime = getResources().getInteger(
//					android.R.integer.config_shortAnimTime);
//
//			mLoginStatusView.setVisibility(View.VISIBLE);
//			mLoginStatusView.animate().setDuration(shortAnimTime)
//					.alpha(showLoggingIn ? 1 : 0)
//					.setListener(new AnimatorListenerAdapter() {
//						@Override
//						public void onAnimationEnd(Animator animation) {
//							mLoginStatusView.setVisibility(showLoggingIn ? View.VISIBLE
//									: View.GONE);
//						}
//					});
//			
//			mLoginInfoView.setVisibility(View.VISIBLE);
//			mLoginInfoView.animate().setDuration(shortAnimTime)
//					.alpha(showOnline ? 1 : 0)
//					.setListener(new AnimatorListenerAdapter() {
//						@Override
//						public void onAnimationEnd(Animator animation) {
//							mLoginInfoView.setVisibility(showOnline ? View.VISIBLE
//									: View.GONE);
//						}
//					});
//
//			mLoginFormView.setVisibility(View.VISIBLE);
//			mLoginFormView.animate().setDuration(shortAnimTime)
//					.alpha(showOffline ? 1 : 0)
//					.setListener(new AnimatorListenerAdapter() {
//						@Override
//						public void onAnimationEnd(Animator animation) {
//							mLoginFormView.setVisibility(showOffline ? View.VISIBLE : View.GONE);
//						}
//					});
//		} else {
		
		// The ViewPropertyAnimator APIs are not available, so simply show
		// and hide the relevant UI components.
		mLoginStatusView.setVisibility(showLoggingIn ? View.VISIBLE : View.GONE);
		mLoginInfoView.setVisibility(showOnline ? View.VISIBLE : View.GONE);
		mLoginFormView.setVisibility(showOffline ? View.VISIBLE : View.GONE);
				
		if (logout_button == null) return;
		if (showOnline) {
			logout_button.setVisible(true);
		}
		else {
			logout_button.setVisible(false);
		}
//		}
	}

	/**
	 * Represents an asynchronous login/registration task used to authenticate
	 * the user.
	 */
	public class UserLoginTask extends AsyncTask<Void, Void, Boolean> {
		@Override
		protected Boolean doInBackground(Void... params) {

			try {
				// Simulate network access.
				Thread.sleep(2000);
			} catch (InterruptedException e) {
				return false;
			}

			if (mEmail.equals("stian@gmail.com")) {
				if (mPassword.equals("qwertyui")) {
					mUserId = 7;
					mToken = "SECURE";
					return true;
				}
			}

			return false;
		}

		@Override
		protected void onPostExecute(final Boolean success) {
			mAuthTask = null;

			if (success) {
				handleLoggedIn();
				updateViews(State.ONLINE);
			} else {
				handleLoggedOut(false);
				mPasswordView.setError(getString(R.string.error_incorrect_password));
				mPassword = "";
				mPasswordView.setText("");
				mPasswordView.requestFocus();
				updateViews(State.OFFLINE);
			}
		}

		@Override
		protected void onCancelled() {
			mAuthTask = null;
			handleLoggedOut(false);
			updateViews(State.OFFLINE);
		}
	}

	public void handleLoggedIn() {
		SharedPreferences.Editor editor = settings.edit();
		editor.putBoolean(SETTINGS_USER_ONLINE, true);
		editor.putString(SETTINGS_USER_MAIL, mEmail);
		editor.putInt(SETTINGS_USER_ID, mUserId);
		editor.putString(SETTINGS_USER_SECURE_TOKEN, mToken);
		editor.commit();
		
		Intent resultIntent = new Intent();
		resultIntent.putExtra(RESULT_EXTRA_STATUS, true); //true = logged in
		setResult(Activity.RESULT_OK, resultIntent);
		finish();
	}
	
	public void handleLoggedOut(boolean finish_activity) {
		SharedPreferences.Editor editor = settings.edit();
		editor.remove(SETTINGS_USER_ONLINE);
		editor.remove(SETTINGS_USER_MAIL);
		editor.remove(SETTINGS_USER_ID);
		editor.remove(SETTINGS_USER_SECURE_TOKEN);
		editor.commit();
		
		if (finish_activity) {
			Intent resultIntent = new Intent();
			resultIntent.putExtra(RESULT_EXTRA_STATUS, false); //false = logged out
			setResult(Activity.RESULT_OK, resultIntent);
			finish();
		}
	}
}
