document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault()

  const login = document.getElementById('login').value
  const password = document.getElementById('password').value

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ login, password }),
      credentials: 'include',
    })

    const data = await response.json()

    if (data.message === 'Logged in') {
      window.location.href = '/'
    } else {
      alert('Ошибка входа')
    }
  } catch (error) {
    console.error('Error:', error)
    alert('Произошла ошибка при входе')
  }
})
