export default async function handler(req, res) {
  const { code } = req.query;
  const { GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET } = process.env;
  
  try {
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        client_id: GITHUB_CLIENT_ID,
        client_secret: GITHUB_CLIENT_SECRET,
        code,
      }),
    });
    
    const data = await response.json();
    
    if (data.error) {
      return res.status(401).send(`GitHub Error: ${data.error_description}`);
    }

    if (!data.access_token) {
      return res.status(401).send('GitHub Error: No access token received');
    }
    
    const script = `
      <script>
        (function() {
          const token = "${data.access_token}";
          const target = window.opener || window.parent;
          if (target) {
            target.postMessage("authorizing:github", "*");
            target.postMessage("authorization:github:success:" + JSON.stringify({ token: token, provider: "github" }), "*");
          } else {
            document.body.innerText = "Error: No target window found.";
          }
        })()
      </script>`;
    
    res.setHeader('Content-Type', 'text/html');
    res.send(script);
  } catch (error) {
    res.status(500).send(error.message);
  }
}