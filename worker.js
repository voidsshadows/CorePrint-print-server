addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return handleOptions();
  } else if (request.method === 'POST') {
    return handlePostRequest(request);
  } else if (request.method === 'GET') {
    return handleGetRequest();
  } else {
    return new Response('Method Not Allowed', { status: 405 });
  }
}

function handleOptions() {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  return new Response(null, {
    headers: headers
  });
}

function sanitizeInput(input) {
  // Basic sanitization to prevent HTML and JavaScript injection
  return input.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

async function hasMessageBeenSent(username, message) {
  try {
    const keys = await quotes.list();
    for (const key of keys.keys) {
      const value = await quotes.get(key.name);
      const quote = JSON.parse(value);
      if (quote.username === username && quote.message === message) {
        return true;
      }
    }
    return false;
  } catch (error) {
    console.error('Error checking if message has been sent:', error);
    return false;
  }
}

async function handlePostRequest(request) {
  try {
    const data = await request.json();
    const { username, message } = data;

    if (!username || !message) {
      return new Response('Username and message are required', { status: 400 });
    }

    // Sanitize inputs to prevent malicious content
    const sanitizedUsername = sanitizeInput(username);
    const sanitizedMessage = sanitizeInput(message);

    // Check if the message has been sent before
    const messageExists = await hasMessageBeenSent(sanitizedUsername, sanitizedMessage);
    if (messageExists) {
      return new Response('Message already sent', { status: 409 });
    }

    const timestamp = Date.now();
    const id = `${sanitizedUsername}-${timestamp}`;

    await quotes.put(id, JSON.stringify({ username: sanitizedUsername, message: sanitizedMessage, timestamp }));

    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    };

    return new Response(JSON.stringify({ message: 'Message saved' }), {
      headers: headers,
      status: 200
    });
  } catch (error) {
    console.error('Error in POST request:', error);
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    };

    return new Response(JSON.stringify({ error: 'Internal Server Error' }), {
      headers: headers,
      status: 500
    });
  }
}

async function handleGetRequest() {
  try {
    const keys = await quotes.list();
    const quotesArray = await Promise.all(
      keys.keys.map(async key => {
        const value = await quotes.get(key.name);
        return JSON.parse(value);
      })
    );

    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    };

    return new Response(JSON.stringify(quotesArray), {
      headers: headers,
      status: 200
    });
  } catch (error) {
    console.error('Error in GET request:', error);
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    };

    return new Response(JSON.stringify({ error: 'Internal Server Error' }), {
      headers: headers,
      status: 500
    });
  }
}
