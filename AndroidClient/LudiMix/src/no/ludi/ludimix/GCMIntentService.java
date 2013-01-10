package no.ludi.ludimix;
import java.util.Set;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.Toast;

import com.google.android.gcm.GCMBaseIntentService;


public class GCMIntentService extends GCMBaseIntentService {

	// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // //
	// http://stackoverflow.com/questions/4443278/toast-sending-message-to-a-handler-on-a-dead-thread  //
	Handler mMainThreadHandler = null;  // // // // // // // // // // // // // // // // // // // // // //
	// // // // // // // // // // // // WHY WHY WHY WHY WHY WHY WHY?? // // // // // // // // // // // //
	// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // //
	
	
    public GCMIntentService() {
        super(GCMIntentService.class.getName());

        mMainThreadHandler = new Handler();
    }

	@Override
	protected void onError(Context context, String errorId) {
		// TODO Auto-generated method stub

	}
	
	@Override
	protected boolean onRecoverableError(Context context, String errorId) {
		// TODO Auto-generated method stub
		return super.onRecoverableError(context, errorId);
	}

	@Override
	protected void onMessage(Context context, Intent intent) {
		Log.v(TAG, "onMessage: " + intent.toString());
		// TODO Auto-generated method stub
		Bundle b = intent.getExtras();
		Set<String> keys = b.keySet();
		for (String key : keys) {
			final Object o = b.get(key);
			Log.i(TAG, "onMessageMsg: k=" + key + " v=" + (String)o);
			if (key.equals("msg")) {

				mMainThreadHandler.post(new Runnable() {
		            @Override
		            public void run() {
		                Toast.makeText(getApplicationContext(), "Received: " + (String)o, Toast.LENGTH_LONG).show();
		            }
		        });
				
				Log.i(TAG, "ShouldToast");
			}
		}
	}

	@Override
	protected void onRegistered(Context context, String registrationId) {
		// TODO Auto-generated method stub
		Log.v(TAG, "onRegister: " + registrationId);
	}

	@Override
	protected void onUnregistered(Context context, String registrationId) {
		// TODO Auto-generated method stub
		Log.v(TAG, "onUnregister: " + registrationId);
	}

}
