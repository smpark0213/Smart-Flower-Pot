package com.example.smartpotandroid

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.example.smartpotandroid.databinding.ActivityMainBinding
import com.example.smartpotandroid.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {

    private lateinit var binding : FragmentHomeBinding
    private lateinit var mainBinding: ActivityMainBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = FragmentHomeBinding.inflate(inflater, container, false)
        mainBinding = ActivityMainBinding.inflate(inflater, container, false)

        /*
        binding.homeWater.setOnClickListener {
            (context as MainActivity).supportFragmentManager.beginTransaction()
                .replace(R.id.main_frame, PlantFragment()).commitAllowingStateLoss()
            mainBinding.mainBnv.selectedItemId = R.id.home;
        }

        binding.homeLight.setOnClickListener {
            (context as MainActivity).supportFragmentManager.beginTransaction()
                .replace(R.id.main_frame, PlantFragment()).commitAllowingStateLoss()
            mainBinding.mainBnv.selectedItemId = R.id.plant;
        }

        binding.homeCamera.setOnClickListener {
            (context as MainActivity).supportFragmentManager.beginTransaction()
                .replace(R.id.main_frame, CameraFragment()).commitAllowingStateLoss()
            mainBinding.mainBnv.selectedItemId = R.id.camera;
        }
         */

        return binding.root
    }
}