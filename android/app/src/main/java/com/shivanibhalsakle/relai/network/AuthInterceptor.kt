package com.shivanibhalsakle.relai.network

import com.google.android.gms.tasks.Tasks
import com.google.firebase.auth.FirebaseAuth
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val currentUser = FirebaseAuth.getInstance().currentUser
        val request = if (currentUser != null) {
            val idToken = Tasks.await(currentUser.getIdToken(false)).token
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $idToken")
                .build()
        } else {
            chain.request()
        }
        return chain.proceed(request)
    }
}