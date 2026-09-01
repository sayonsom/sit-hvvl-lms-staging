'use client';

import React, { useEffect, useState, useRef, Component } from "react";
import { useParams } from 'react-router-dom';
import axios from 'axios';
import AppLayout from "./AppLayout";
import { SparklesIcon, HandThumbDownIcon, HandThumbUpIcon } from '@heroicons/react/20/solid';
import { ArrowsPointingOutIcon, ArrowsPointingInIcon } from '@heroicons/react/20/solid';
import confetti from 'canvas-confetti';
import { Tab } from '@headlessui/react';
import { Card, Button, Spinner } from 'flowbite-react';
import ModuleViewer from "../components/ModuleViewer";
import MarkdownContent from "../components/MarkdownContent";
import ExperimentFormParameteric from "../components/ExperimentFormParameteric";
import ModuleAssignmentsForm from "../components/ModuleAssignmentsForm";
import VideoCard from "../components/VideoCard";
import { API_URL } from "../env";

class ModelErrorBoundary extends Component {
    constructor(props) { super(props); this.state = { hasError: false }; }
    static getDerivedStateFromError() { return { hasError: true }; }
    componentDidUpdate(previousProps) {
        if (previousProps.resetKey !== this.props.resetKey && this.state.hasError) {
            this.setState({ hasError: false });
        }
    }
    render() {
        if (this.state.hasError) {
            return (
                <div className="flex items-center justify-center h-full text-gray-500">
                    <div className="text-center">
                        <p className="text-lg font-medium">3D model could not be loaded</p>
                        <p className="text-sm mt-2">The model file may not be available in this environment.</p>
                    </div>
                </div>
            );
        }
        return this.props.children;
    }
}

const apiUrl = API_URL;

function classNames(...classes) {
    return classes.filter(Boolean).join(' ');
}

export default function ModuleDetailPage() {
    const { moduleID } = useParams();
    const [module, setModule] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isRephrasing, setIsRephrasing] = useState(false);
    const [isFunFactFinding, setIsFunFactFinding] = useState(false);
    const [rephraseCount, setRephraseCount] = useState(0);
    const [funfactCount, setFunFactCount] = useState(0);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [selectedTab, setSelectedTab] = useState(0);
    const modelContainerRef = useRef(null);

    const triggerConfetti = () => {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    };

    const rephraseConcept = async () => {
        if (rephraseCount >= 5) return;

        setIsRephrasing(true);
        try {
            const response = await axios.post(`${apiUrl}/rephrase/`, null, {
                params: { text: module.concept }
            });
            setModule({ ...module, concept: response.data.rephrased_text });
            setRephraseCount(rephraseCount + 1);
            triggerConfetti();
        } catch (error) {
            console.error('Error rephrasing concept', error);
            alert("Error rephrasing concept", error);
        } finally {
            setIsRephrasing(false);
        }
    };

    const tellAFunFact = async () => {
        if (funfactCount >= 5) return;

        setIsFunFactFinding(true);
        setModule({ ...module, fun_fact: '' });
        try {
            const response = await axios.post(`${apiUrl}/funfact/`, null, {
                params: { text: module.title }
            });
            setModule({ ...module, fun_fact: response.data.fun_fact });
            setFunFactCount(funfactCount + 1);
            triggerConfetti();
        } catch (error) {
            console.error('Error finding a new fun fact', error);
            alert("Error finding a new fun fact", error);
        } finally {
            setIsFunFactFinding(false);
        }
    };

    const toggleFullscreen = () => {
        if (!isFullscreen) {
            if (modelContainerRef.current.requestFullscreen) {
                modelContainerRef.current.requestFullscreen();
            } else if (modelContainerRef.current.mozRequestFullScreen) {
                modelContainerRef.current.mozRequestFullScreen();
            } else if (modelContainerRef.current.webkitRequestFullscreen) {
                modelContainerRef.current.webkitRequestFullscreen();
            } else if (modelContainerRef.current.msRequestFullscreen) {
                modelContainerRef.current.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }
        setIsFullscreen(!isFullscreen);
    };

    useEffect(() => {
        const fetchCourseDetails = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get(`${apiUrl}/modules/${moduleID}`);
                setModule(response.data);
            } catch (error) {
                console.error('Error fetching course details', error);
                setError(error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCourseDetails();
    }, [moduleID]);

    if (isLoading) {
        return (
            <AppLayout>
                <Spinner />
            </AppLayout>
        );
    }

    if (error) {
        return (
            <AppLayout>
                <div className="max-w-md w-full space-y-8">
                    <div className="flex flex-col items-center">
                        <p>Sorry, there was an error loading this page</p>
                    </div>
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout>
            {/* PAGE HEADING */}
            <div className="min-h-full">
                <div className="bg-white dark:bg-gray-800 px-6 py-10 lg:px-8">
                    <div className="mx-auto max-w-3xl text-base leading-7 text-gray-700 dark:text-gray-200">
                        <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100 sm:text-5xl font-heading">{module.title}</h1>
                        <p className="mt-4 text-xl text-gray-500 dark:text-gray-200 font-heading">{module.description}</p>
                    </div>
                </div>

                <div className="font-sans px-6 md:px-8 mt-10">
                    <Tab.Group defaultIndex={0} onChange={(index) => setSelectedTab(index)}>
                        <Tab.List className="flex space-x-1 rounded-t-lg bg-gray-100 dark:bg-gray-800 p-1">
                            <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                Theory (In-depth)
                            </Tab>
                            <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                3D Model
                            </Tab>
                            <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                Experiment
                            </Tab>


                        <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                Core Concept
                            </Tab>

                            <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                Fun Fact
                            </Tab>
                            <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                Quiz
                            </Tab>
                            <Tab className={({ selected }) =>
                                classNames(
                                    'w-full py-2.5 text-sm leading-5 font-medium text-blue-700 rounded-lg',
                                    selected ? 'bg-white shadow text-red-600 underline' : 'text-blue-900 hover:bg-white/[0.12] hover:text-red-600'
                                )
                            }>
                                Video
                            </Tab>
                        </Tab.List>

                        <Tab.Panels className="mt-4">
                            <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg">
                                <Card className="max-w-full my-4 shadow-xl">
                                    <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                                        Theory (In-depth)
                                    </h5>
                                    <div className="mt-4">
                                        <MarkdownContent contentURL={module.theory} />
                                    </div>
                                </Card>
                            </Tab.Panel>

                            <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg" ref={modelContainerRef} style={{ height: '80vh', position: 'relative' }}>
                                {selectedTab === 1 && (
                                    <>
                                        <ModelErrorBoundary resetKey={module.interactive_file}>
                                            <ModuleViewer url={module.interactive_file} />
                                        </ModelErrorBoundary>
                                        <Button
                                            size="xs"
                                            onClick={toggleFullscreen}
                                            className="absolute top-2 right-2 z-10"
                                            gradientDuoTone="purpleToPink"
                                        >
                                            {isFullscreen ? (
                                                <ArrowsPointingInIcon className="h-5 w-5" />
                                            ) : (
                                                <ArrowsPointingOutIcon className="h-5 w-5" />
                                            )}
                                        </Button>
                                    </>
                                )}
                            </Tab.Panel>

                           

                        <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg">
                        <Card className="max-w-full shadow-lg">
                        <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                            Experiment
                        </h5>
                        <div className="exp">
                            <ExperimentFormParameteric url={module.plottingexperimentconfig}/>
                            </div>
                        </Card>
                            </Tab.Panel>

                            <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg">
                                <Card className="max-w-full my-4 shadow-xl">
                                    <div className="flex justify-between">
                                        <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                                            Core Concept
                                        </h5>

                                        {rephraseCount < 5 ? (
                                            <Button size="xs" gradientDuoTone="purpleToPink" onClick={rephraseConcept} disabled={isRephrasing}>
                                                <SparklesIcon className="mr-2 h-5 w-5" />
                                                Explain another way
                                            </Button>
                                        ) : (
                                            <Button size="xs" disabled={true}>
                                                Out of Explanations
                                            </Button>
                                        )}
                                    </div>

                                    {isRephrasing ? (
                                        <Spinner />
                                    ) : (
                                        <p className="mt-4 font-normal text-gray-700 dark:text-gray-400 text-base">
                                            {module?.concept}
                                        </p>
                                    )}
                                    {module?.concept && !isRephrasing && (
                                        <div className="text-center my-4">
                                            <Button color="green" size="xs">
                                                <HandThumbUpIcon className="mr-2 h-5 w-5" />
                                            </Button>
                                            <Button color="red" size="xs">
                                                <HandThumbDownIcon className="mr-2 h-5 w-5" />
                                            </Button>
                                        </div>
                                    )}
                                </Card>
                            </Tab.Panel>

                            <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg">
                                <Card className="max-w-full mt-4 shadow-lg">
                                    <div>
                                        <div className="flex justify-between">
                                            <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                                                Fun Fact
                                            </h5>
                                            <Button size="xs" gradientDuoTone="purpleToPink" onClick={tellAFunFact} disabled={isFunFactFinding}>
                                                <SparklesIcon className="mr-2 h-5 w-5" />
                                                Tell me another one
                                            </Button>
                                        </div>
                                    </div>

                                    <p className="font-normal text-gray-700 dark:text-gray-400 text-base whitespace-pre-line">
                                        {module.fun_fact}
                                    </p>
                                </Card>
                            </Tab.Panel>

                            <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg">
                                <Card className="max-w-full mt-4 shadow-lg">
                                    <div>
                                        <div className="flex justify-between">
                                            <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                                                Quiz
                                            </h5>
                                        </div>
                                        <ModuleAssignmentsForm moduleID={moduleID} />
                                    </div>
                                </Card>
                            </Tab.Panel>

                            <Tab.Panel className="bg-white dark:bg-gray-800 p-4 rounded-b-lg">
                                <VideoCard videoLink={module.video_link_1} />
                            </Tab.Panel>
                        </Tab.Panels>
                    </Tab.Group>
                </div>
            </div>
        </AppLayout>
    );
}
