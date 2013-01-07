package no.ludi.ludimix;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gcm.GCMRegistrar;

public class MainActivity extends Activity {

	static final private int LOGIN_ACTIVITY_RETURNED = 0;
	static final private int SETTINGS_ACTIVITY_RETURNED = 1;
	
	static final private String TAG = "MainActivity";
	static final private String SENDER_ID = "919676944722";
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		GCMRegistrar.checkDevice(this);
		GCMRegistrar.checkManifest(this);
		final String regId = GCMRegistrar.getRegistrationId(this);
		if (regId.equals("")) {
			Log.v(TAG, "Registering");
		  GCMRegistrar.register(this, SENDER_ID);
		} else {
		  Log.v(TAG, "Already registered");
		}
		
		setContentView(R.layout.activity_main);
		TextView txt_loggedInAs = (TextView)findViewById(R.id.loggedInAs);
		SharedPreferences settings = getSharedPreferences("login_data", 0);
	    
		int userid = settings.getInt("user_id", 0);
	    String username = settings.getString("user_mail", "");
		txt_loggedInAs.setText("Brukernavn: " + username);
		Toast.makeText(this, "BYGGE", Toast.LENGTH_SHORT).show();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// TODO Auto-generated method stub
		switch (item.getItemId()){
	        case R.id.menu_login:
	        	Intent loginIntent = new Intent(this, LoginActivity.class);
	        	startActivityForResult(loginIntent, LOGIN_ACTIVITY_RETURNED);
		        break;
	        case R.id.menu_settings:
	        	Intent settingsIntent = new Intent(this, SettingsActivity.class);
	        	startActivityForResult(settingsIntent, SETTINGS_ACTIVITY_RETURNED);
		        break;
		    default:
		    	Toast.makeText(this, "Unknown item...", Toast.LENGTH_SHORT).show();
		    	break;
        }
		return true;
	}

	@Override 
	public void onActivityResult(int requestCode, int resultCode, Intent data) {     
		super.onActivityResult(requestCode, resultCode, data); 
		switch(requestCode) { 
			case LOGIN_ACTIVITY_RETURNED:
				if (resultCode == Activity.RESULT_OK) { 
					boolean status = data.getBooleanExtra(LoginActivity.RESULT_EXTRA_STATUS, false);
					if (status) {
						// TODO LOGGED IN
						Toast.makeText(this, "LOGGED IN", Toast.LENGTH_SHORT).show();
					}
					else {
						// TODO LOGGED OUT
						Toast.makeText(this, "LOGGED OUT", Toast.LENGTH_SHORT).show();
					}
				}
				else {
					// TODO LOGIN ABORTED
					Toast.makeText(this, "LOGIN ABORTED", Toast.LENGTH_SHORT).show();
				}
				break; 
			case SETTINGS_ACTIVITY_RETURNED:
				if (resultCode == Activity.RESULT_OK) { 
					// TODO SETTINGS OK
					Toast.makeText(this, "SETTINGS OK", Toast.LENGTH_SHORT).show();
				}
				else {
					// TODO SETTINGS ABORTED
					Toast.makeText(this, "SETTINGS ABORTED", Toast.LENGTH_SHORT).show();
				}
				break; 
		} 
	}
	
}
