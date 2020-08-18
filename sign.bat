REM SET CERT_PASSWORD=
signtool sign /debug /t http://timestamp.verisign.com/scripts/timstamp.dll /f cert\FellowConsultingCert.p12 /p %CERT_PASSWORD% dist\QuickdataLoad.exe
