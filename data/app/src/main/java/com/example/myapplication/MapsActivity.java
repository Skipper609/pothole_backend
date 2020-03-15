package com.example.myapplication;

import androidx.appcompat.app.AlertDialog;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import android.Manifest;
import android.content.Context;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.hardware.TriggerEventListener;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Environment;
import android.provider.CalendarContract;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.CircleOptions;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;

public class MapsActivity extends FragmentActivity implements OnMapReadyCallback, SensorEventListener, LocationListener  {

    private GoogleMap mMap;
    private SensorManager sensorManager;
    private Sensor accsensor,gyrosensor;
    private TriggerEventListener triggerEventListener;
    TextView xView,yView,zView;
    protected LocationManager locationManager;
    protected LocationListener locationListener;
    protected Context context;
    private boolean recording = false;
    float speed;
    private float acc[] = new float[3];
    private float gyro[] = new float[3];
    TextView txtLat;
    LatLng latLng;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        accsensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        gyrosensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        xView = (TextView) findViewById(R.id.xval);
        yView = (TextView) findViewById(R.id.yval);
        zView = (TextView) findViewById(R.id.zval);
        txtLat = (TextView) findViewById(R.id.coords);

        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {

            // Should we show an explanation?
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                    Manifest.permission.ACCESS_FINE_LOCATION)) {

                // Show an explanation to the user *asynchronously* -- don't block
                // this thread waiting for the user's response! After the user
                // sees the explanation, try again to request the permission.
                new AlertDialog.Builder(this)
                        .setTitle("Need Location")
                        .setMessage("Me wants to know ur location")
                        .setPositiveButton("OK", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialogInterface, int i) {
                                //Prompt the user once explanation has been shown
                                ActivityCompat.requestPermissions(MapsActivity.this,
                                        new String[]{Manifest.permission.ACCESS_FINE_LOCATION},
                                        10);
                            }
                        })
                        .create()
                        .show();


            } else {
                // No explanation needed, we can request the permission.
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.ACCESS_FINE_LOCATION},
                        10);
            }

        }
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED)
        {
            locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0, 0, (LocationListener) this);
        }


    }


    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
    }
    @Override
    public void onLocationChanged(Location location) {
        txtLat.setText("Latitude:" + location.getLatitude() + ", Longitude:" + location.getLongitude());
        latLng = new LatLng(location.getLatitude(),location.getLongitude());
        speed = location.getSpeed();
        setMapView();
    }
    public  void setMapView(){
        mMap.clear();
        mMap.addCircle(new CircleOptions()
                .center(latLng)
                .radius(10) // radius in meters
                .fillColor(Color.BLUE));
        mMap.addCircle(new CircleOptions()
                .center(latLng)
                .radius(40) // radius in meters
                .strokeColor(Color.BLUE)
        .strokeWidth(5));
        mMap.animateCamera(CameraUpdateFactory.newLatLngZoom(latLng, 16.0f),100,null);
    }

    @Override
    public void onProviderDisabled(String provider) {
        Log.d("Latitude","disable");
    }

    @Override
    public void onProviderEnabled(String provider) {
        Log.d("Latitude","enable");
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
        Log.d("Latitude","status");
    }

    //sensor functions
    @Override
    protected void onPause() {
        super.onPause();
        //sensorManager.unregisterListener(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        sensorManager.registerListener(new SensorEventListener() {
            @Override
            public void onSensorChanged(SensorEvent sensorEvent) {
                if(sensorEvent.sensor.getType() == Sensor.TYPE_ACCELEROMETER){
                    xView.setText("" + sensorEvent.values[0]);
                    yView.setText("" + sensorEvent.values[1]);
                    zView.setText("" + sensorEvent.values[2]);
                    acc[0] = sensorEvent.values[0];
                    acc[1] = sensorEvent.values[1];
                    acc[2] = sensorEvent.values[2];
                    writeFile();
                }
            }

            @Override
            public void onAccuracyChanged(Sensor sensor, int i) {

            }
        }, accsensor, sensorManager.SENSOR_DELAY_NORMAL);
        sensorManager.registerListener(new SensorEventListener() {
            @Override
            public void onSensorChanged(SensorEvent sensorEvent) {
                if(sensorEvent.sensor.getType() == Sensor.TYPE_GYROSCOPE){

                    gyro[0] = sensorEvent.values[0];
                    gyro[1] = sensorEvent.values[1];
                    gyro[2] = sensorEvent.values[2];
                    writeFile();
                }
            }

            @Override
            public void onAccuracyChanged(Sensor sensor, int i) {

            }
        }, gyrosensor, sensorManager.SENSOR_DELAY_NORMAL);
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
    }
    public void writeFile(){
        if(recording) {

            try {
                String FILENAME = "sensordata.txt";
                File folder = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                File myFile = new File(folder, FILENAME);
                FileOutputStream fstream = new FileOutputStream(myFile,true);

                //FileWriter f = new FileWriter("sensor.txt", true);
                String s = System.currentTimeMillis() / 10 + "," + Float.toString(acc[0]) + "," + Float.toString(acc[1]) + "," + Float.toString(acc[2]) +
                        "," + Float.toString(gyro[0]) + "," + Float.toString(gyro[1]) + "," + Float.toString(gyro[2]) + "," + latLng.longitude + "," + latLng.latitude + ","
                         + speed + "\n";
                fstream.write(s.getBytes());

                //Toast.makeText(getApplicationContext(), "Details Saved in "+myFile.getAbsolutePath(), Toast.LENGTH_SHORT).show();
                fstream.close();

            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    public void writePothole(View v){
        if(recording) {
            try {
                String FILENAME = "pothole.txt";
                File folder = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                File myFile = new File(folder, FILENAME);
                FileOutputStream fstream = new FileOutputStream(myFile,true);

                //FileWriter f = new FileWriter("sensor.txt", true);
                String s = System.currentTimeMillis() / 10 + "," + latLng.longitude + "," + latLng.latitude + "," + "pothole" + "\n";
                fstream.write(s.getBytes());

                //Toast.makeText(getApplicationContext(), "Details Saved in "+myFile.getAbsolutePath(), Toast.LENGTH_SHORT).show();
                fstream.close();

            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }
    public void toggleOn(View v){
        Button b = findViewById(R.id.start_stop);
        if(!recording){
            b.setText("END");
            Toast.makeText(getApplicationContext(), "Data Recording Started", Toast.LENGTH_SHORT).show();
            recording = true;
        }
        else{
            b.setText("START");
            Toast.makeText(getApplicationContext(), "Data Recording Stopped", Toast.LENGTH_SHORT).show();
            recording = false;
        }
    }

}
