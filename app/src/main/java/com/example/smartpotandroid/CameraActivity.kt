package com.example.smartpotandroid

import android.os.Bundle
import android.view.LayoutInflater
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.smartpotandroid.databinding.ActivityCameraBinding

class CameraActivity : AppCompatActivity() {

    lateinit var binding: ActivityCameraBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityCameraBinding.inflate(layoutInflater)

        binding.cameraBackBtn.setOnClickListener {
            Toast.makeText(this, "back", Toast.LENGTH_SHORT).show()
            finish()
        }

        binding.moveLeftBtn.setOnClickListener {
            Toast.makeText(this, "moveLeft", Toast.LENGTH_SHORT).show()
        }

        binding.waterBtn.setOnClickListener {
            Toast.makeText(this, "water", Toast.LENGTH_SHORT).show()
        }

        binding.moveRightBtn.setOnClickListener {
            Toast.makeText(this, "moveRight", Toast.LENGTH_SHORT).show()
        }

        binding.movePot1Btn.setOnClickListener {
            Toast.makeText(this, "movePot1", Toast.LENGTH_SHORT).show()
        }

        binding.movePot2Btn.setOnClickListener {
            Toast.makeText(this, "movePot2", Toast.LENGTH_SHORT).show()
        }

        binding.movePot3Btn.setOnClickListener {
            Toast.makeText(this, "movePot3", Toast.LENGTH_SHORT).show()
        }

        setContentView(binding.root)
    }
}