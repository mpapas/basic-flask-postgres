$compress = @{
    Path = "*.py", "requirements.txt", "static", "templates"
    CompressionLevel = "Fastest"
    DestinationPath = "Deployment.zip"
  }

Compress-Archive -Force @compress
