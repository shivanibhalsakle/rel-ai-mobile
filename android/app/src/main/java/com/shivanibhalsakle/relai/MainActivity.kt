package com.shivanibhalsakle.relai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.shivanibhalsakle.relai.ui.theme.RelaiTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RelaiTheme {
                val appViewModel: AppViewModel = viewModel()
                val appState by appViewModel.uiState.collectAsStateWithLifecycle()

                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    when (val state = appState) {
                        AppUiState.Loading -> {
                            Box(
                                modifier = Modifier.fillMaxSize().padding(innerPadding),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator()
                            }
                        }
                        else -> {
                            val navController = rememberNavController()
                            NavHost(
                                navController = navController,
                                startDestination = when (state) {
                                    AppUiState.NeedsSignIn -> "signIn"
                                    AppUiState.NeedsOnboarding -> "onboarding"
                                    AppUiState.Ready -> "home"
                                    AppUiState.Loading -> "signIn"
                                },
                                modifier = Modifier.padding(innerPadding)
                            ) {
                                composable("signIn") {
                                    SignInScreen(onSignedIn = { appViewModel.checkStartState() })
                                }
                                composable("onboarding") {
                                    // next step: real onboarding form goes here
                                }
                                composable("home") {
                                    // placeholder for now
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}