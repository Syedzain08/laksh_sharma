export default async function handler(req, res) {
  const { GITHUB_CLIENT_ID } = process.env;
  

  const params = new URLSearchParams({
    client_id: GITHUB_CLIENT_ID,
    scope: 'repo',
    redirect_uri: 'https://laksh-sharma.vercel.app/api/callback',
    allow_signup: 'true'
  });
  
  res.redirect(`https://github.com/login/oauth/authorize?${params.toString()}`);
}