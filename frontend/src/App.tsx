import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './components/ui/button';
import { Progress } from './components/ui/progress';
import { removeBackground } from './lib/utils';

function App() {
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [isOnline, setIsOnline] = useState(true);

  // Check online status
  useEffect(() => {
    function handleOnlineStatusChange() {
      setIsOnline(navigator.onLine);
    }

    window.addEventListener('online', handleOnlineStatusChange);
    window.addEventListener('offline', handleOnlineStatusChange);
    
    return () => {
      window.removeEventListener('online', handleOnlineStatusChange);
      window.removeEventListener('offline', handleOnlineStatusChange);
    };
  }, []);

  const processImage = useCallback(async (file: File) => {
    if (!file) return;
    
    // Reset states
    setError(null);
    setProgress(0);
    setProcessedImage(null);
    setIsProcessing(true);
    
    try {
      // Simulate progress since we don't have real-time progress from the API
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) { // Cap at 90% until we get actual completion
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);
      
      // Process the image
      const result = await removeBackground(file);
      
      // Clear the interval and set progress to 100%
      clearInterval(progressInterval);
      setProgress(100);
      setProcessedImage(result);
      setRetryCount(0); // Reset retry count on success
    } catch (err) {
      console.error('Error processing image:', err);
      
      if (!navigator.onLine) {
        setError('Sie sind offline. Bitte stellen Sie eine Verbindung zum Internet her.');
      } else {
        setError('Der Server ist momentan ausgelastet, bitte versuchen Sie es später erneut.');
      }
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    if (currentFile && retryCount < 3) {
      setRetryCount(prev => prev + 1);
      processImage(currentFile);
    } else if (retryCount >= 3) {
      setError('Zu viele Versuche. Bitte laden Sie ein anderes Bild hoch oder versuchen Sie es später erneut.');
    }
  }, [currentFile, retryCount, processImage]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    
    // Only accept image files
    if (!file.type.startsWith('image/')) {
      setError('Bitte laden Sie nur Bilddateien hoch.');
      return;
    }
    
    // Check if user is online
    if (!navigator.onLine) {
      setError('Sie sind offline. Bitte stellen Sie eine Verbindung zum Internet her.');
      return;
    }
    
    // Display the original image
    const objectUrl = URL.createObjectURL(file);
    setOriginalImage(objectUrl);
    setCurrentFile(file);
    setRetryCount(0);
    
    processImage(file);
  }, [processImage]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp'],
    },
    disabled: isProcessing,
    maxFiles: 1,
  });

  return (
    <div className="min-h-screen bg-background flex flex-col items-center">
      <header className="w-full py-4 sm:py-6 px-4 border-b">
        <div className="container flex justify-between items-center">
          <h1 className="text-xl sm:text-2xl font-bold">Hintergrund Entfernen</h1>
          <div className="flex items-center">
            {!isOnline && (
              <div className="flex items-center mr-4 text-destructive">
                <AlertCircle className="w-4 h-4 mr-1" />
                <span className="text-xs">Offline</span>
              </div>
            )}
            <a 
              href="https://github.com/your-username/remove-bg" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              GitHub
            </a>
          </div>
        </div>
      </header>
      
      <main className="container flex-1 py-4 sm:py-8 px-4 max-w-5xl">
        <div className="mb-4 sm:mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-2">Bild hochladen</h2>
          <p className="text-sm sm:text-base text-muted-foreground">
            Laden Sie ein Bild hoch, um den Hintergrund zu entfernen. Unterstützt JPG, PNG und WebP.
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-8">
          {/* Upload zone */}
          <div>
            <div 
              {...getRootProps()} 
              className={`border-2 border-dashed rounded-lg p-4 sm:p-8 h-60 sm:h-80 flex flex-col items-center justify-center cursor-pointer transition-colors ${
                isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="w-8 h-8 sm:w-12 sm:h-12 text-muted-foreground mb-4" />
              {isDragActive ? (
                <p className="text-center text-base sm:text-lg">Bild hier ablegen...</p>
              ) : (
                <p className="text-center text-sm sm:text-lg">
                  Ziehen Sie ein Bild hierher oder klicken Sie zum Auswählen
                </p>
              )}
              <p className="text-xs sm:text-sm text-muted-foreground mt-2">
                Maximal 12 MP pro Bild
              </p>
            </div>
            
            {originalImage && (
              <div className="mt-4">
                <h3 className="text-base sm:text-lg font-medium mb-2">Originalbild</h3>
                <div className="relative border rounded-lg overflow-hidden h-48 sm:h-64 bg-muted/30">
                  <img 
                    src={originalImage} 
                    alt="Original" 
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>
            )}
          </div>
          
          {/* Result zone */}
          <div>
            <div className="border rounded-lg p-4 sm:p-6 h-60 sm:h-80 flex flex-col items-center justify-center bg-muted/10">
              {isProcessing ? (
                <>
                  <Loader2 className="w-8 h-8 sm:w-12 sm:h-12 text-primary mb-4 animate-spin" />
                  <p className="text-base sm:text-lg mb-4">Hintergrund wird entfernt...</p>
                  <div className="w-full max-w-md">
                    <Progress value={progress} className="h-2" />
                    <p className="text-xs sm:text-sm text-muted-foreground text-right mt-1">
                      {progress}%
                    </p>
                  </div>
                </>
              ) : processedImage ? (
                <>
                  <div className="relative w-full h-full">
                    <img 
                      src={processedImage} 
                      alt="Ohne Hintergrund" 
                      className="w-full h-full object-contain"
                    />
                  </div>
                  <div className="mt-4 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                    <Button 
                      onClick={() => {
                        const a = document.createElement('a');
                        a.href = processedImage;
                        a.download = 'entfernt-hintergrund.png';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                      }}
                      className="w-full sm:w-auto"
                    >
                      Herunterladen
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => {
                        setOriginalImage(null);
                        setProcessedImage(null);
                        setProgress(0);
                        setCurrentFile(null);
                      }}
                      className="w-full sm:w-auto"
                    >
                      Neues Bild
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  {error ? (
                    <div className="flex flex-col items-center">
                      <AlertCircle className="w-8 h-8 sm:w-12 sm:h-12 text-destructive mb-4" />
                      <p className="text-base sm:text-lg text-center mb-4">
                        {error}
                      </p>
                      {currentFile && retryCount < 3 && (
                        <Button 
                          variant="outline" 
                          onClick={handleRetry}
                          className="mt-2 flex items-center"
                        >
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Erneut versuchen ({retryCount + 1}/3)
                        </Button>
                      )}
                    </div>
                  ) : (
                    <>
                      <ImageIcon className="w-8 h-8 sm:w-12 sm:h-12 text-muted-foreground mb-4" />
                      <p className="text-base sm:text-lg text-center">
                        Ihr Ergebnis wird hier angezeigt
                      </p>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </main>
      
      <footer className="w-full py-4 sm:py-6 px-4 border-t mt-auto">
        <div className="container text-center text-xs sm:text-sm text-muted-foreground">
          <p>Open-Source Projekt | Verarbeitung erfolgt lokal | Keine Daten werden gespeichert</p>
        </div>
      </footer>
    </div>
  );
}

export default App;