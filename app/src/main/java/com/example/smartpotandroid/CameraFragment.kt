package com.example.smartpotandroid

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.alexvas.rtsp.widget.RtspSurfaceView
import com.example.smartpotandroid.databinding.FragmentCameraBinding
import java.io.File
import java.io.FileNotFoundException
import java.io.FileOutputStream


class CameraFragment : Fragment() {

    private lateinit var binding : FragmentCameraBinding

    private val uri: Uri = Uri.parse("rtsp://172.16.227.64:8554/unicast")
    private val username = ""
    private val password = ""

    // 0 = Pause  |  1 = Play
    var flag = 0

    lateinit var toastMsg : Toast

    // private val CAPTURE_PATH = "/CAPTURE_TEST"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        super.onCreate(savedInstanceState)

        binding = FragmentCameraBinding.inflate(layoutInflater)

        binding.cameraVideo.init(uri, username, password)

        toastMsg = Toast.makeText(context, "null", Toast.LENGTH_SHORT)

        val listener = object: RtspSurfaceView.RtspStatusListener {
            override fun onRtspFirstFrameRendered() {
                Log.d("CameraActivity", "First Frame Rendered")
                toastMsg.setText("Complete!")
                toastMsg.show()
            }

            override fun onRtspStatusConnected() {
                toastMsg.setText("Wait...")
                toastMsg.show()
                binding.cameraPlay.visibility = View.GONE
                binding.cameraPause.visibility = View.VISIBLE
                flag = 1
                Log.d("CameraActivity", "Status Connected")
            }

            override fun onRtspStatusConnecting() {
                Log.d("CameraActivity", "Connecting..")
            }

            override fun onRtspStatusDisconnected() {
                Log.d("CameraActivity", "Disconnected")
                toastMsg.setText("Failed!! Please Reload!!")
                binding.cameraPlay.visibility = View.VISIBLE
                binding.cameraPause.visibility = View.GONE
                flag = 0
            }

            override fun onRtspStatusFailed(message: String?) {
                Log.e("CameraActivity", "Failed ${message}")
            }

            override fun onRtspStatusFailedUnauthorized() {
                Log.d("CameraActivity", "Unauthorized")
            }
        }

        binding.cameraVideo.setStatusListener(listener)

        binding.cameraPlay.setOnClickListener {
            flag = 1
            binding.cameraVideo.start(requestAudio = false, requestVideo = true)
            binding.cameraPlay.visibility = View.GONE
            binding.cameraPause.visibility = View.VISIBLE
        }

        binding.cameraPause.setOnClickListener {
            flag = 0
            binding.cameraVideo.stop()
            binding.cameraPlay.visibility = View.VISIBLE
            binding.cameraPause.visibility = View.GONE
            // captureView(binding.cameraVideo)
        }

        binding.cameraResetBtn.setOnClickListener {
            Toast.makeText(context, "Loading...", Toast.LENGTH_LONG).show()
            binding.cameraVideo.stop()

            if (flag == 0) {
                binding.cameraPlay.visibility = View.GONE
                binding.cameraPause.visibility = View.VISIBLE
            }

            flag = 1
            binding.cameraVideo.start(requestAudio = false, requestVideo = true)
        }

        return binding.root
    }

    /**
     * 특정 뷰만 캡쳐
     * @param View
     */
    /*
    fun captureView(View: View) {
        View.buildDrawingCache()
        val captureView = View.drawingCache
        val fos: FileOutputStream
        val strFolderPath = Environment.getExternalStorageDirectory().absolutePath + CAPTURE_PATH
        val folder = File(strFolderPath)
        if (!folder.exists()) {
            folder.mkdirs()
        }
        val strFilePath = strFolderPath + "/" + System.currentTimeMillis() + ".png"
        Log.d("CameraFragment", strFilePath)
        val fileCacheItem = File(strFilePath)
        try {
            fos = FileOutputStream(Environment.getExternalStorageDirectory().toString()+"/capture.jpeg")
            captureView.compress(Bitmap.CompressFormat.PNG, 100, fos)
        } catch (e: FileNotFoundException) {
            e.printStackTrace()
        }
    }
     */

}