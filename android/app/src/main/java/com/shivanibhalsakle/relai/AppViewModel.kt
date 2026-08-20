package com.shivanibhalsakle.relai

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.firebase.auth.FirebaseAuth
import com.shivanibhalsakle.relai.network.RetrofitClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

sealed interface AppUiState {
    data object Loading : AppUiState
    data object NeedsSignIn : AppUiState
    data object NeedsOnboarding : AppUiState
    data object Ready : AppUiState
}

class AppViewModel : ViewModel() {

    private val _uiState = MutableStateFlow<AppUiState>(AppUiState.Loading)
    val uiState: StateFlow<AppUiState> = _uiState

    init {
        checkStartState()
    }

    fun checkStartState() {
        _uiState.value = AppUiState.Loading
        viewModelScope.launch {
            val currentUser = FirebaseAuth.getInstance().currentUser
            if (currentUser == null) {
                _uiState.value = AppUiState.NeedsSignIn
                return@launch
            }

            try {
                val status = RetrofitClient.apiService.getOnboardingStatus()
                _uiState.value = if (status.onboardingCompleted) {
                    AppUiState.Ready
                } else {
                    AppUiState.NeedsOnboarding
                }
            } catch (e: Exception) {
                _uiState.value = AppUiState.NeedsSignIn
            }
        }
    }
}