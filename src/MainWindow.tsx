import { FunctionComponent } from "react";
import ApplicationBar, { applicationBarHeight } from "./ApplicationBar";
import AboutPage from "./pages/AboutPage/AboutPage";
import HomePage from "./pages/HomePage/HomePage";
import useRoute from "./useRoute";
import useWindowDimensions from "./useWindowDimensions";
import DandiBrowser from "./pages/DandiBrowser/DandiBrowser";
import ProjectPage from "./pages/ProjectPage/ProjectPage";
import ComputeResourcesPage from "./pages/ComputeResourcePage/ComputeResourcePage";

type Props = {
    // none
}

const MainWindow: FunctionComponent<Props> = () => {
    const {route} = useRoute()
    const {width, height} = useWindowDimensions()
    return (
        <div style={{position: 'absolute', width, height, overflow: 'hidden'}}>
            <div style={{position: 'absolute', width, height: applicationBarHeight}}>
                <ApplicationBar />
            </div>
            <div style={{position: 'absolute', top: applicationBarHeight, width, height: height - applicationBarHeight}}>
                {
                    route.page === 'home' ? (
                        <HomePage width={width} height={height - applicationBarHeight} />
                    ) : (route.page === 'dandisets' || route.page === 'dandiset') ? (
                        <DandiBrowser width={width} height={height - applicationBarHeight} />
                    ) : route.page === 'project' ? (
                        <ProjectPage width={width} height={height - applicationBarHeight} />
                    ) : route.page === 'about' ? (
                        <AboutPage width={width} height={height - applicationBarHeight} />
                    ) : route.page === 'compute-resource' ? (
                        <ComputeResourcesPage
                            width={width}
                            height={height - applicationBarHeight}
                            computeResourceId={route.computeResourceId}
                        />
                    ) : (
                        <div>404</div>
                    )
                }
            </div>
        </div>
    )
}

export default MainWindow