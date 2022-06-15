package com.example.smartpotandroid

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout.OnRefreshListener
import com.example.smartpotandroid.databinding.FragmentPlantBinding
import com.google.firebase.firestore.FirebaseFirestore
import com.google.type.DateTime
import java.lang.String
import java.sql.Types.TIMESTAMP
import java.util.*
import kotlin.Int
import kotlin.toString


class PlantFragment : Fragment() {

    private lateinit var binding : FragmentPlantBinding

    private var plantDatas = ArrayList<FlowerData>()
    val db = FirebaseFirestore.getInstance()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = FragmentPlantBinding.inflate(inflater, container, false)

        var plantAdapter = PlantRVAdapter(plantDatas)
        binding.plantRv.adapter = plantAdapter
        binding.plantRv.layoutManager = LinearLayoutManager(context, LinearLayoutManager.VERTICAL, false)

        dataRead(plantAdapter)

        binding.plantSwipe.setOnRefreshListener(OnRefreshListener { /* swipe 시 진행할 동작 */
            dataRead(plantAdapter)
            // cnt_text.setText(String.valueOf(++cnt))
            binding.plantSwipe.isRefreshing = false
        })

        binding.plantResetBtn.setOnClickListener {
            dataRead(plantAdapter)
        }

        return binding.root
    }

    private fun dataRead(plantAdapter: PlantRVAdapter) {
        db.collection("sensordata").get().addOnSuccessListener { result ->
            val plantList: ArrayList<FlowerData> = arrayListOf<FlowerData>()
            var name = ""
            var img: Int? = 0
            var moisture = ""
            var light = ""
            for (document in result) {
                val timestamp = document["updatedAt"] as com.google.firebase.Timestamp
                val dateArr = timestamp.toDate().toString().split(" ")
                var date = dateArr[1] + " " + dateArr[2] + ", " + dateArr[5] + " " + dateArr[0] + " " + dateArr[3]
                Log.d("dateCheck", date)

                binding.plantTime.text = date

                name = when(document.id) {
                    "flowerpot1" -> "방울토마토"
                    "flowerpot2" -> "강낭콩"
                    "flowerpot3" -> "허브바질"
                    else -> "error"
                }

                img = when(document.id) {
                    "flowerpot1" -> R.drawable.plant1
                    "flowerpot2" -> R.drawable.plant2
                    "flowerpot3" -> R.drawable.plant3
                    else -> null
                }

                var lightData = document["light"].toString().toDouble()
                light = when {
                    lightData < 0F -> "Error"
                    0F < lightData && lightData < 400F -> "LOW"
                    400F < lightData && lightData < 600F -> "MIDDLE"
                    else -> "HIGH"
                }

                var moistureData = document["moisture"].toString().toDouble()
                moisture = when {
                    moistureData < 0F -> "Error"
                    0F < moistureData && moistureData < 300F -> "LOW"
                    300F < moistureData && moistureData < 700F -> "MIDDLE"
                    else -> "HIGH"
                }

                plantList.add(FlowerData(name, img, light, moisture))
            }
            plantAdapter.addAll(plantList)
        }
            .addOnFailureListener {
                Toast.makeText(context, "Connection Failed", Toast.LENGTH_SHORT).show()
            }
    }
}