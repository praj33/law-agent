import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Html, Sphere, Box } from '@react-three/drei';
import * as THREE from 'three';

interface TalkingAvatarProps {
  position?: [number, number, number];
  scale?: number;
  onSpeak?: (text: string) => void;
}

const TalkingAvatar: React.FC<TalkingAvatarProps> = ({ 
  position = [0, 0, 0], 
  scale = 1,
  onSpeak 
}) => {
  const avatarRef = useRef<THREE.Group>(null);
  const headRef = useRef<THREE.Mesh>(null);
  const mouthRef = useRef<THREE.Mesh>(null);
  const eyeLeftRef = useRef<THREE.Mesh>(null);
  const eyeRightRef = useRef<THREE.Mesh>(null);
  
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isHovered, setIsHovered] = useState(false);
  const [blinkTimer, setBlinkTimer] = useState(0);

  // Legal assistant messages
  const legalMessages = [
    "Welcome to the virtual courtroom! I'm your legal assistant.",
    "I can help you understand court procedures and legal processes.",
    "Would you like to learn about different types of legal cases?",
    "The judge's bench is the central authority in this courtroom.",
    "Legal proceedings follow strict protocols and procedures.",
    "I'm here to guide you through the complexities of law.",
    "Each element in this courtroom has specific legal significance.",
    "Feel free to ask me any questions about legal matters!"
  ];

  // Speaking animation and message cycling
  useEffect(() => {
    const speakingInterval = setInterval(() => {
      if (!isSpeaking) {
        const randomMessage = legalMessages[Math.floor(Math.random() * legalMessages.length)];
        setCurrentMessage(randomMessage);
        setIsSpeaking(true);
        onSpeak?.(randomMessage);

        // Stop speaking after message duration
        setTimeout(() => {
          setIsSpeaking(false);
          setCurrentMessage('');
        }, 4000 + randomMessage.length * 50); // Dynamic duration based on message length
      }
    }, 8000); // Speak every 8 seconds

    return () => clearInterval(speakingInterval);
  }, [isSpeaking, onSpeak]);

  // Animation frame
  useFrame((state) => {
    if (avatarRef.current) {
      // Gentle floating animation
      avatarRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
      
      // Head slight rotation when speaking
      if (headRef.current && isSpeaking) {
        headRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 3) * 0.1;
        headRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 2) * 0.05;
      }

      // Mouth animation when speaking
      if (mouthRef.current && isSpeaking) {
        const mouthScale = 1 + Math.sin(state.clock.elapsedTime * 8) * 0.3;
        mouthRef.current.scale.setScalar(mouthScale);
      } else if (mouthRef.current) {
        mouthRef.current.scale.setScalar(1);
      }

      // Blinking animation
      setBlinkTimer(prev => prev + 0.016);
      if (blinkTimer > 3) { // Blink every 3 seconds
        if (eyeLeftRef.current && eyeRightRef.current) {
          const blinkScale = Math.max(0.1, Math.sin(state.clock.elapsedTime * 20));
          eyeLeftRef.current.scale.y = blinkScale;
          eyeRightRef.current.scale.y = blinkScale;
        }
        if (blinkTimer > 3.2) setBlinkTimer(0);
      } else {
        if (eyeLeftRef.current && eyeRightRef.current) {
          eyeLeftRef.current.scale.y = 1;
          eyeRightRef.current.scale.y = 1;
        }
      }

      // Hover effect
      if (isHovered) {
        avatarRef.current.scale.setScalar(scale * 1.1);
      } else {
        avatarRef.current.scale.setScalar(scale);
      }
    }
  });

  const handleClick = () => {
    if (!isSpeaking) {
      const randomMessage = legalMessages[Math.floor(Math.random() * legalMessages.length)];
      setCurrentMessage(randomMessage);
      setIsSpeaking(true);
      onSpeak?.(randomMessage);

      setTimeout(() => {
        setIsSpeaking(false);
        setCurrentMessage('');
      }, 4000 + randomMessage.length * 50);
    }
  };

  return (
    <group 
      ref={avatarRef} 
      position={position}
      onClick={handleClick}
      onPointerOver={() => setIsHovered(true)}
      onPointerOut={() => setIsHovered(false)}
    >
      {/* Body */}
      <Box
        position={[0, -1, 0]}
        args={[0.8, 1.5, 0.4]}
      >
        <meshStandardMaterial color="#2563eb" />
      </Box>

      {/* Head */}
      <Sphere
        ref={headRef}
        position={[0, 0.5, 0]}
        args={[0.5, 32, 32]}
      >
        <meshStandardMaterial color="#fdbcb4" />
      </Sphere>

      {/* Hair */}
      <Sphere
        position={[0, 0.8, -0.1]}
        args={[0.55, 32, 32]}
      >
        <meshStandardMaterial color="#8b4513" />
      </Sphere>

      {/* Eyes */}
      <Sphere
        ref={eyeLeftRef}
        position={[-0.15, 0.6, 0.4]}
        args={[0.08, 16, 16]}
      >
        <meshStandardMaterial color="#000000" />
      </Sphere>
      <Sphere
        ref={eyeRightRef}
        position={[0.15, 0.6, 0.4]}
        args={[0.08, 16, 16]}
      >
        <meshStandardMaterial color="#000000" />
      </Sphere>

      {/* Nose */}
      <Box
        position={[0, 0.5, 0.45]}
        args={[0.05, 0.1, 0.05]}
      >
        <meshStandardMaterial color="#fdbcb4" />
      </Box>

      {/* Mouth */}
      <Sphere
        ref={mouthRef}
        position={[0, 0.35, 0.4]}
        args={[0.1, 16, 8]}
      >
        <meshStandardMaterial color={isSpeaking ? "#ff6b6b" : "#ff8a8a"} />
      </Sphere>

      {/* Professional Badge */}
      <Box
        position={[0, -0.5, 0.25]}
        args={[0.3, 0.2, 0.05]}
      >
        <meshStandardMaterial color="#ffd700" />
      </Box>

      {/* Name Tag */}
      <Text
        position={[0, -0.5, 0.3]}
        fontSize={0.08}
        color="black"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        Legal Assistant
      </Text>

      {/* Speech Bubble */}
      {isSpeaking && currentMessage && (
        <Html position={[0, 1.5, 0]} center>
          <div className="bg-white/95 backdrop-blur-sm rounded-lg p-3 border border-gray-200 shadow-lg max-w-xs">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <p className="text-sm text-gray-800 font-medium leading-relaxed">
                {currentMessage}
              </p>
            </div>
            {/* Speech bubble tail */}
            <div className="absolute bottom-[-8px] left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-l-transparent border-r-transparent border-t-white/95"></div>
          </div>
        </Html>
      )}

      {/* Hover Tooltip */}
      {isHovered && !isSpeaking && (
        <Html position={[0, 1.2, 0]} center>
          <div className="bg-black/80 text-white px-3 py-2 rounded-lg text-sm">
            Click to talk with me!
          </div>
        </Html>
      )}

      {/* Ambient light for the avatar */}
      <pointLight position={[0, 2, 1]} intensity={0.5} color="#ffffff" />
      <spotLight
        position={[0, 3, 2]}
        angle={0.3}
        penumbra={0.5}
        intensity={0.8}
        color="#ffeaa7"
        target-position={[0, 0, 0]}
      />
    </group>
  );
};

export default TalkingAvatar;
