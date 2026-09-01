import React, { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useLoader, useThree } from '@react-three/fiber';
import { Bounds, Center, ContactShadows, OrbitControls } from '@react-three/drei';
import axios from 'axios';
import { Button, Spinner } from 'flowbite-react';
import * as THREE from 'three';
import { TbAugmentedReality2 } from "react-icons/tb";
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import dracoDecoder from 'three/examples/jsm/libs/draco/draco_decoder.js?raw';
import { API_URL } from "../env";

function getModelErrorMessage(error) {
  if (error?.response?.status === 404) return 'The configured 3D model file is missing from storage.';
  if (error?.response?.status === 403) return 'The 3D model file could not be accessed.';
  return error?.message || 'The model file may not be available in this environment.';
}

function resolveSignedUrl(fileUrl) {
  if (!fileUrl || typeof window === 'undefined') return fileUrl || '';
  try {
    const apiOrigin = new URL(API_URL || window.location.origin, window.location.origin).origin;
    return new URL(fileUrl, apiOrigin).toString();
  } catch (_error) {
    return fileUrl;
  }
}

function isTransientRecoveryModel(url) {
  return String(url || '').toLowerCase().includes('highvoltage_trv');
}

function CeramicBushing({ position, rotation = [0, 0, 0] }) {
  return (
    <group position={position} rotation={rotation}>
      <mesh castShadow receiveShadow>
        <cylinderGeometry args={[0.11, 0.14, 1.25, 28]} />
        <meshStandardMaterial color="#d7e6ed" roughness={0.42} metalness={0.05} />
      </mesh>
      {[-0.48, -0.32, -0.16, 0, 0.16, 0.32, 0.48].map((offset) => (
        <mesh key={offset} position={[0, offset, 0]} castShadow receiveShadow>
          <cylinderGeometry args={[0.23, 0.23, 0.045, 28]} />
          <meshStandardMaterial color="#f1f7fa" roughness={0.32} metalness={0.04} />
        </mesh>
      ))}
      <mesh position={[0, 0.72, 0]} castShadow>
        <cylinderGeometry args={[0.045, 0.045, 0.35, 16]} />
        <meshStandardMaterial color="#b87333" roughness={0.22} metalness={0.8} />
      </mesh>
    </group>
  );
}

function TransientRecoveryVoltageModel() {
  return (
    <group rotation={[0, -0.28, 0]}>
      <mesh position={[0, -1.04, 0]} receiveShadow>
        <boxGeometry args={[5.6, 0.16, 3.2]} />
        <meshStandardMaterial color="#365269" roughness={0.82} metalness={0.18} />
      </mesh>
      <mesh position={[0, -0.72, 0]} castShadow receiveShadow>
        <boxGeometry args={[2.6, 0.55, 1.35]} />
        <meshStandardMaterial color="#27627a" roughness={0.4} metalness={0.42} />
      </mesh>
      <mesh position={[0, -0.37, 0]} castShadow>
        <boxGeometry args={[2.15, 0.2, 0.95]} />
        <meshStandardMaterial color="#182f3d" roughness={0.38} metalness={0.58} />
      </mesh>
      <CeramicBushing position={[-0.72, 0.35, 0]} />
      <CeramicBushing position={[0.72, 0.35, 0]} />
      <mesh position={[0, 1.05, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
        <cylinderGeometry args={[0.055, 0.055, 1.44, 16]} />
        <meshStandardMaterial color="#c47d36" roughness={0.2} metalness={0.82} />
      </mesh>
      <mesh position={[0, -0.72, 0.76]} castShadow>
        <boxGeometry args={[0.72, 0.38, 0.18]} />
        <meshStandardMaterial color="#f4b942" emissive="#4a2600" emissiveIntensity={0.14} roughness={0.5} />
      </mesh>
      <mesh position={[-2, -0.48, -0.3]} castShadow>
        <cylinderGeometry args={[0.5, 0.5, 1.05, 28]} />
        <meshStandardMaterial color="#744da9" roughness={0.38} metalness={0.3} />
      </mesh>
      <mesh position={[-2, 0.13, -0.3]} castShadow>
        <torusGeometry args={[0.36, 0.075, 14, 36]} />
        <meshStandardMaterial color="#d5c5ef" roughness={0.35} metalness={0.16} />
      </mesh>
      <mesh position={[2, -0.38, -0.2]} castShadow>
        <boxGeometry args={[0.78, 1.22, 0.9]} />
        <meshStandardMaterial color="#bb4d4d" roughness={0.48} metalness={0.22} />
      </mesh>
      {[[-1.85, 0.6, -0.3], [1.62, 0.75, -0.05]].map((point, index) => (
        <mesh key={index} position={point} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.035, 0.035, index === 0 ? 1.55 : 1.15, 12]} />
          <meshStandardMaterial color="#d28b42" roughness={0.22} metalness={0.78} />
        </mesh>
      ))}
    </group>
  );
}

function Model3D({ url, highVisibility }) {
  const gltf = useLoader(GLTFLoader, url, (loader) => {
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderConfig({ type: 'js' });
    dracoLoader._loadLibrary = (libraryUrl) => {
      if (libraryUrl === 'draco_decoder.js') return Promise.resolve(dracoDecoder);
      return Promise.reject(new Error(`Unsupported Draco decoder asset: ${libraryUrl}`));
    };
    dracoLoader.preload();
    loader.setDRACOLoader(dracoLoader);
  });

  const scene = useMemo(() => {
    const clone = gltf.scene.clone(true);
    if (!highVisibility) return clone;

    clone.traverse((object) => {
      if (!object.isMesh || !object.material) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      const enhanced = materials.map((sourceMaterial) => {
        const material = sourceMaterial.clone();
        if (material.color) {
          const brightestChannel = Math.max(material.color.r, material.color.g, material.color.b);
          if (brightestChannel < 0.32) material.color.lerp(new THREE.Color('#aebdca'), 0.58);
        }
        if (typeof material.metalness === 'number') material.metalness = Math.min(material.metalness, 0.62);
        if (typeof material.roughness === 'number') material.roughness = Math.max(material.roughness, 0.3);
        material.needsUpdate = true;
        return material;
      });
      object.material = Array.isArray(object.material) ? enhanced : enhanced[0];
      object.castShadow = true;
      object.receiveShadow = true;
    });
    return clone;
  }, [gltf, highVisibility]);

  return <primitive object={scene} />;
}

function Background() {
  const { scene } = useThree();
  useEffect(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 2;
    canvas.height = 64;
    const context = canvas.getContext('2d');
    const gradient = context.createLinearGradient(0, 0, 0, 64);
    gradient.addColorStop(0, '#dfeaf2');
    gradient.addColorStop(0.58, '#89a6ba');
    gradient.addColorStop(1, '#344e61');
    context.fillStyle = gradient;
    context.fillRect(0, 0, 2, 64);
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    scene.background = texture;
    return () => texture.dispose();
  }, [scene]);
  return null;
}

function ModuleViewer({ url }) {
  const controlsRef = useRef();
  const [signedUrl, setSignedUrl] = useState('');
  const [error, setError] = useState(null);
  const usesBuiltInModel = isTransientRecoveryModel(url);
  const highVisibility = String(url || '').toLowerCase().includes('cockroft');

  useEffect(() => {
    let active = true;
    const getSignedUrl = async () => {
      if (!url) {
        setError(new Error('No model file configured for this module.'));
        setSignedUrl('');
        return;
      }
      if (usesBuiltInModel) {
        setError(null);
        setSignedUrl('built-in:transient-recovery-voltage');
        return;
      }

      try {
        setError(null);
        setSignedUrl('');
        const response = await axios.get(`${API_URL}/generate-signed-url/`, {
          params: { blob_name: url },
        });
        if (active) setSignedUrl(resolveSignedUrl(response.data.url));
      } catch (requestError) {
        console.error('Error generating model URL', requestError);
        if (active) setError(new Error(getModelErrorMessage(requestError)));
      }
    };
    getSignedUrl();
    return () => { active = false; };
  }, [url, usesBuiltInModel]);

  if (error) {
    return (
      <div className="relative flex h-full w-full items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700" data-testid="model-error">
        <div className="text-center text-gray-500 dark:text-gray-300">
          <p className="text-lg font-medium">3D model could not be loaded</p>
          <p className="mt-2 text-sm">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full overflow-hidden rounded-lg" data-testid="model-viewer">
      <Button className="absolute right-4 top-4 z-10">
        View in AR/VR
        <TbAugmentedReality2 className="ml-2" />
      </Button>
      {usesBuiltInModel ? (
        <div className="pointer-events-none absolute bottom-4 left-4 z-10 rounded-md bg-slate-950/75 px-3 py-2 text-xs text-white">
          Circuit breaker TRV test arrangement · drag to rotate · scroll to zoom
        </div>
      ) : null}
      {!usesBuiltInModel && !signedUrl ? (
        <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center gap-3 bg-slate-900/35 text-sm font-medium text-white">
          <Spinner size="sm" />
          Loading 3D model…
        </div>
      ) : null}

      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [4.6, 3.2, 6.8], fov: 44 }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.35 }}
      >
        <ambientLight intensity={1.25} />
        <hemisphereLight args={['#ffffff', '#274052', 1.7]} />
        <directionalLight position={[6, 8, 5]} intensity={2.2} castShadow />
        <directionalLight position={[-5, 4, -4]} intensity={1.35} />
        <pointLight position={[0, 3, 4]} intensity={1.1} distance={18} />
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.25}>
            <Center>
              {usesBuiltInModel ? (
                <TransientRecoveryVoltageModel />
              ) : signedUrl ? (
                <Model3D key={signedUrl} url={signedUrl} highVisibility={highVisibility} />
              ) : null}
            </Center>
          </Bounds>
          <ContactShadows position={[0, -1.13, 0]} opacity={0.42} scale={8} blur={2.8} far={5} />
        </Suspense>
        <OrbitControls ref={controlsRef} makeDefault minDistance={2.2} maxDistance={14} />
        <Background />
      </Canvas>
    </div>
  );
}

export default ModuleViewer;
