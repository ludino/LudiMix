package no.ludi.ludimix;
import java.util.Set;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

import com.google.android.gcm.GCMBaseIntentService;


public class GCMIntentService extends GCMBaseIntentService {

	@Override
	protected void onError(Context ctx, String arg) {
		// TODO Auto-generated method stub

	}
	
	@Override
	protected boolean onRecoverableError(Context ctx, String errorId) {
		// TODO Auto-generated method stub
		return super.onRecoverableError(ctx, errorId);
	}

	@Override
	protected void onMessage(Context ctx, Intent arg) {
		Log.v(TAG, "onMessage: " + arg.toString());
		// TODO Auto-generated method stub
		Bundle b = arg.getExtras();
		Set<String> keys = b.keySet();
		for (String key : keys) {
			Object o = b.get(key);
			String type = o.getClass().toString();
			Log.i(TAG, "onMessageMsg: k=" + key + " v=" + (String)o);
		}
	}

	@Override
	protected void onRegistered(Context ctx, String arg) {
		// TODO Auto-generated method stub
		Log.v(TAG, "onRegister: " + arg.toString());
	}

	@Override
	protected void onUnregistered(Context ctx, String arg) {
		// TODO Auto-generated method stub
		Log.v(TAG, "onUnregister: " + arg.toString());
	}

}
