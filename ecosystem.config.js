const path = require("path"); // Make sure this is at the top

module.exports = {
  apps: [
    /*{
      name: "js-fe", //front end never got developer so im leaving this here
      script: "node_modules/next/dist/bin/next",
      args: "dev",
      cwd: "./js-fe",
      shell: true,
    },*/
    {
      name: "py-be",
      cwd: "./py-be",
      script: path.resolve(
        __dirname,
        "py-be",
        ".venv",
        "Scripts",
        "pythonw.exe"
      ),
      watch: true,
      ignore_watch: [".venv", "node_modules", "__pycache__", ".git"],
      args: "-m uvicorn src.main:app --host 0.0.0.0 --port 8001",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
  ],
};
