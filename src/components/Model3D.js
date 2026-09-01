import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { useGLTF, Clone } from '@react-three/drei';

export default function Model3D({ url }) {

    
    // const glb = useGLTF(url);
    
    // alert("GLB Loaded")  
    // console.log(glb);

    //   return (
    //     <>
    //         <Clone object={glb.scene} scale = {4} position={-1} />
    //     </>
          
          
    //   );

    // const gltf = useLoader(GLTFLoader, url, loader => {
    //     const dracoLoader = new DRACOLoader();
    //     dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
    //     loader.setDRACOLoader(dracoLoader);
    // });

    // return <primitive object={gltf.scene} />;

    console.log("URL: ", url);

    return (
        // <Clone object={useGLTF(url).scene} scale = {4} position={-1} />
        <></>
    )

}

