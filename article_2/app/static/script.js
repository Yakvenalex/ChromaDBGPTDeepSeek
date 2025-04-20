marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: false,
  gfm: true,
  headerIds: true,
  mangle: false,
})

function createLoadingIndicator() {
  const loadingDiv = document.createElement('div')
  loadingDiv.className = 'loading'
  loadingDiv.innerHTML = `
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
        `
  return loadingDiv
}

function addMessage(content, isUser = false) {
  const chatOutput = document.getElementById('chatOutput')
  const messageDiv = document.createElement('div')
  messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`

  const copyButton = document.createElement('button')
  copyButton.className = 'copy-button'
  copyButton.innerHTML = '<i class="bi bi-clipboard"></i>'
  copyButton.onclick = () => {
    navigator.clipboard.writeText(content).then(() => {
      copyButton.innerHTML = '<i class="bi bi-check"></i>'
      copyButton.classList.add('copied')
      setTimeout(() => {
        copyButton.innerHTML = '<i class="bi bi-clipboard"></i>'
        copyButton.classList.remove('copied')
      }, 2000)
    })
  }

  const contentDiv = document.createElement('div')
  contentDiv.className = 'message-content'
  contentDiv.innerHTML = marked.parse(content)

  messageDiv.appendChild(contentDiv)
  messageDiv.appendChild(copyButton)
  chatOutput.appendChild(messageDiv)
  chatOutput.scrollTop = chatOutput.scrollHeight
  return messageDiv
}

function updateMessage(messageDiv, content) {
  const copyButton = messageDiv.querySelector('.copy-button')
  const contentDiv =
    messageDiv.querySelector('.message-content') ||
    document.createElement('div')
  contentDiv.className = 'message-content'
  contentDiv.innerHTML = marked.parse(content)

  if (!messageDiv.querySelector('.message-content')) {
    messageDiv.innerHTML = ''
    messageDiv.appendChild(contentDiv)
    messageDiv.appendChild(copyButton)
  }

  messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

document
  .getElementById('queryInput')
  .addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      document.getElementById('sendButton').click()
    }
  })

document.getElementById('sendButton').addEventListener('click', async () => {
  const query = document.getElementById('queryInput').value.trim()
  const provider = document.getElementById('provider').value
  const chatOutput = document.getElementById('chatOutput')
  const sendButton = document.getElementById('sendButton')
  const queryInput = document.getElementById('queryInput')

  if (!query) {
    alert('Введите запрос!')
    return
  }

  addMessage(query, true)
  queryInput.value = ''
  sendButton.disabled = true

  const loadingIndicator = createLoadingIndicator()
  chatOutput.appendChild(loadingIndicator)
  chatOutput.scrollTop = chatOutput.scrollHeight

  try {
    const response = await fetch('/api/ask_with_ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response: query, provider }),
    })

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login'
        return
      }
      throw new Error('Ошибка сервера')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let currentText = ''

    chatOutput.removeChild(loadingIndicator)
    const assistantMessage = addMessage('')
    assistantMessage.classList.add('streaming')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Обрабатываем буфер посимвольно
      while (buffer.length > 0) {
        const char = buffer[0]
        buffer = buffer.slice(1)
        currentText += char

        // Обновляем сообщение каждые 50мс
        await new Promise((resolve) => setTimeout(resolve, 50))
        updateMessage(assistantMessage, currentText)
      }
    }

    assistantMessage.classList.remove('streaming')
    if (currentText.trim() === '{"response":"Ничего не найдено"}') {
      updateMessage(assistantMessage, 'Ничего не найдено')
    }
  } catch (error) {
    chatOutput.removeChild(loadingIndicator)
    addMessage(`Ошибка: ${error.message}`)
  } finally {
    sendButton.disabled = false
    queryInput.focus()
  }
})

document.getElementById('logoutButton').addEventListener('click', async () => {
  try {
    const response = await fetch('/api/logout', {
      method: 'POST',
      credentials: 'include',
    })

    if (response.ok) {
      window.location.href = '/login'
    }
  } catch (error) {
    console.error('Ошибка при выходе:', error)
  }
})
