"use client"

import React, { useState, useEffect, useRef } from 'react';
import { getAIResponse } from '../services/openaiService';
import styles from './SmarterAssistant.module.css';

const SmarterAssistant: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [context, setContext] = useState<string[]>([]);
  const [isQuestion, setIsQuestion] = useState(false);
  const [aiResponse, setAIResponse] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Reference to SpeechRecognition object
  const recognitionRef = useRef<any>(null);
  
  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event: any) => {
          const current = event.resultIndex;
          const sentence = event.results[current][0].transcript;
          setTranscript(sentence);
          
          // Check if it's a question
          const containsQuestion = sentence.includes('?');
          setIsQuestion(containsQuestion);
          
          if (containsQuestion) {
            handleQuestion(sentence);
          } else {
            setContext(prev => [...prev, sentence]);
          }
        };
        
        recognition.onerror = (event: any) => {
          console.error('Speech recognition error', event.error);
          setIsListening(false);
        };
        
        recognitionRef.current = recognition;
      } else {
        alert('Your browser does not support speech recognition.');
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        setIsListening(false);
      }
    };
  }, []);
  
  const handleQuestion = async (question: string) => {
    setIsProcessing(true);
    try {
      const response = await getAIResponse(question, context);
      setAIResponse(response.split('->').map(item => item.trim()));
      setContext([response]); // Set the response as the new context
      setIsQuestion(false);
    } catch (error) {
      console.error('Error getting AI response:', error);
      setAIResponse(['Error occurred. Please try again.']);
    } finally {
      setIsProcessing(false);
    }
  };
  
  const toggleListening = () => {
    if (!recognitionRef.current) return;
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error('Failed to start speech recognition:', err);
      }
    }
  };
  
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Smarter Assistant</h1>
      
      <div className={styles.controlSection}>
        <button 
          onClick={toggleListening}
          className={`${styles.button} ${isListening ? styles.buttonStop : styles.buttonStart}`}
        >
          {isListening ? 'Stop Listening' : 'Start Listening'}
        </button>
      </div>
      
      <div className={styles.transcriptSection}>
        <h2 className={styles.sectionTitle}>Transcript:</h2>
        <div className={styles.transcriptBox}>
          {transcript || "Speak to see transcript here"}
        </div>
      </div>
      
      {isProcessing && (
        <div className={styles.processingSection}>
          <p className={styles.thinking}>Thinking...</p>
        </div>
      )}
      
      {aiResponse.length > 0 && (
        <div className={styles.responseSection}>
          <h2 className={styles.sectionTitle}>Response:</h2>
          <div className={styles.responseBox}>
            {aiResponse.map((line, index) => (
              <p key={index} className={styles.responseLine}>{line}</p>
            ))}
          </div>
        </div>
      )}
      
      <div className={styles.contextSection}>
        <h3 className={styles.sectionTitle}>Conversation Context:</h3>
        <div className={styles.contextBox}>
          {context.length > 0 ? 
            context.map((item, index) => (
              <p key={index} className={styles.contextItem}>{item}</p>
            )) : 
            <p className={styles.emptyState}>No conversation context yet</p>
          }
        </div>
      </div>
    </div>
  );
};

export default SmarterAssistant;
