package com.example.smartpotandroid

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import com.example.smartpotandroid.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)

        binding.mainBnv.selectedItemId = R.id.home;

        initBottomNavigation()

        binding.homeWater.setOnClickListener {
            supportFragmentManager.beginTransaction()
                .replace(R.id.main_frame, PlantFragment()).commitAllowingStateLoss()
            binding.mainBnv.selectedItemId = R.id.plant;
        }

        binding.homeLight.setOnClickListener {
            supportFragmentManager.beginTransaction()
                .replace(R.id.main_frame, PlantFragment()).commitAllowingStateLoss()
            binding.mainBnv.selectedItemId = R.id.plant;
        }

        binding.homeCamera.setOnClickListener {
            supportFragmentManager.beginTransaction()
                .replace(R.id.main_frame, CameraFragment()).commitAllowingStateLoss()
            binding.mainBnv.selectedItemId = R.id.camera;
        }

        setContentView(binding.root)
    }

    private fun initBottomNavigation() {

        supportFragmentManager.beginTransaction()
            .replace(R.id.main_frame, HomeFragment())
            .commitAllowingStateLoss()

        binding.mainBnv.setOnNavigationItemSelectedListener setOnItemSelectedListener@{ item ->
            when (item.itemId) {
                R.id.camera -> {
                    binding.homeWater.visibility = View.GONE
                    binding.homeLight.visibility = View.GONE
                    binding.homeCamera.visibility = View.GONE
                    supportFragmentManager.beginTransaction()
                        .replace(R.id.main_frame, CameraFragment())
                        .commitAllowingStateLoss()
                    return@setOnItemSelectedListener true
                }
                R.id.home -> {
                    binding.homeWater.visibility = View.VISIBLE
                    binding.homeLight.visibility = View.VISIBLE
                    binding.homeCamera.visibility = View.VISIBLE
                    supportFragmentManager.beginTransaction()
                        .replace(R.id.main_frame, HomeFragment())
                        .commitAllowingStateLoss()
                    return@setOnItemSelectedListener true
                }
                R.id.plant -> {
                    binding.homeWater.visibility = View.GONE
                    binding.homeLight.visibility = View.GONE
                    binding.homeCamera.visibility = View.GONE
                    supportFragmentManager.beginTransaction()
                        .replace(R.id.main_frame, PlantFragment())
                        .commitAllowingStateLoss()
                    return@setOnItemSelectedListener true
                }
            }
            false
        }
    }
}