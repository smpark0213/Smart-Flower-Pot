package com.example.smartpotandroid

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.smartpotandroid.databinding.ItemPotBinding

class PlantRVAdapter(private var itemList: ArrayList<FlowerData>): RecyclerView.Adapter<PlantRVAdapter.ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PlantRVAdapter.ViewHolder {
        val binding: ItemPotBinding = ItemPotBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun getItemCount(): Int = itemList.size

    override fun onBindViewHolder(holder: PlantRVAdapter.ViewHolder, position: Int) {
        holder.bind(itemList[position])
    }

    inner class ViewHolder(val binding: ItemPotBinding): RecyclerView.ViewHolder(binding.root) {
        fun bind(item: FlowerData) {
            binding.potName.text = item.name
            binding.itemImg.setImageResource(item.img!!)
            binding.itemLight.text = item.light
            binding.itemMoisture.text = item.moisture
        }
    }

    fun addAll(list: ArrayList<FlowerData>) {
        itemList.clear()
        itemList.addAll(list)
        notifyDataSetChanged()
    }
}