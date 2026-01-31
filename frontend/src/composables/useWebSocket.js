import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
const RECONNECT_INTERVAL = 3000
const MAX_RECONNECT_ATTEMPTS = 5

export function useWebSocket() {
  const socket = ref(null)
  const isConnected = ref(false)
  const streamData = ref([])
  const reconnectAttempts = ref(0)
  const reconnectTimer = ref(null)

  const handleMessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (!data.type && data['type!status']) {
        data.type = data['type!status']
        if (!data.data) {
          data.data = { error: data.message || '未知错误' }
        }
      }
      streamData.value.push(data)
    } catch (error) {
      console.error('WebSocket message parse error:', error)
    }
  }

  const handleOpen = () => {
    isConnected.value = true
    reconnectAttempts.value = 0
    console.log('WebSocket connected')
    ElMessage.success('已连接到服务器')
  }

  const handleClose = () => {
    isConnected.value = false
    console.log('WebSocket disconnected')

    if (reconnectAttempts.value < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts.value++
      console.log(`Attempting to reconnect... (${reconnectAttempts.value}/${MAX_RECONNECT_ATTEMPTS})`)
      
      reconnectTimer.value = setTimeout(() => {
        connect()
      }, RECONNECT_INTERVAL)
    } else {
      ElMessage.error('无法连接到服务器，请刷新页面重试')
    }
  }

  const handleError = (error) => {
    console.error('WebSocket error:', error)
    ElMessage.error('连接错误，正在尝试重新连接...')
  }

  const connect = () => {
    if (socket.value) {
      socket.value.close()
    }

    try {
      socket.value = new WebSocket(WS_URL)
      socket.value.onopen = handleOpen
      socket.value.onmessage = handleMessage
      socket.value.onclose = handleClose
      socket.value.onerror = handleError
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      ElMessage.error('无法创建WebSocket连接')
    }
  }

  const disconnect = () => {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }

    if (socket.value) {
      socket.value.close()
      socket.value = null
    }

    isConnected.value = false
  }

  const send = (message) => {
    if (socket.value && isConnected.value) {
      try {
        socket.value.send(JSON.stringify(message))
      } catch (error) {
        console.error('Failed to send message:', error)
        ElMessage.error('发送消息失败')
      }
    } else {
      ElMessage.warning('未连接到服务器，请稍后再试')
    }
  }

  const clearStream = () => {
    streamData.value = []
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    streamData,
    send,
    connect,
    disconnect,
    clearStream
  }
}
