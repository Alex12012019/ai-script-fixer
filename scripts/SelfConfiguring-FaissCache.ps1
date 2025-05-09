
Write-Host "[INFO] Начинаю подготовку кэша..."
$filePath = "D:\faiss_cache\file.exe"
$url = "https://example.com/file.exe"

# Скачивание файла
Invoke-WebRequest -Uri $url -OutFile $filePath -UseBasicParsing

# Проверка существования файла
if (-not (Test-Path $filePath)) {
    Write-Host "[ERROR] Файл не был загружен: $filePath"
    exit
}

# Вычисление SHA256 хеша
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$fileBytes = [IO.File]::ReadAllBytes($filePath)
$hashBytes = $sha256.ComputeHash($fileBytes)
$hashString = [BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()

Write-Host "[INFO] SHA256 хеш файла: $hashString"