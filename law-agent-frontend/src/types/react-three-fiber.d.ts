import { extend } from '@react-three/fiber'
import * as THREE from 'three'

// Extend the Three.js catalog for React Three Fiber
extend({
  // Geometries
  BoxGeometry: THREE.BoxGeometry,
  SphereGeometry: THREE.SphereGeometry,
  CylinderGeometry: THREE.CylinderGeometry,
  PlaneGeometry: THREE.PlaneGeometry,
  
  // Materials
  MeshStandardMaterial: THREE.MeshStandardMaterial,
  MeshBasicMaterial: THREE.MeshBasicMaterial,
  
  // Objects
  Mesh: THREE.Mesh,
  Group: THREE.Group,
  
  // Lights
  AmbientLight: THREE.AmbientLight,
  PointLight: THREE.PointLight,
  SpotLight: THREE.SpotLight,
  DirectionalLight: THREE.DirectionalLight,
})

// This file ensures Three.js elements are available in JSX
export {}
