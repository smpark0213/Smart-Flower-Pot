package com.example.smartpotandroid

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import com.example.smartpotandroid.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        binding = ActivityMainBinding.inflate(layoutInflater)

        binding.mainCameraBtn.setOnClickListener {
            Toast.makeText(this, "Go to Camera", Toast.LENGTH_SHORT).show()
            Log.d("test", "check")
            startActivity(Intent(this, CameraActivity::class.java))
        }

        binding.test.setOnClickListener {
            Log.d("test", "test1")
        }
    }
}