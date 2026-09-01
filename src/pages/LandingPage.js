import { ChevronRightIcon } from '@heroicons/react/20/solid'
import LoginButton from '../components/LoginButton'
import { Link } from "react-router-dom";
import { isAadConfigured } from "../authConfig";

export default function LandingPage() {
  return (
    <div className="bg-white min-h-screen flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-6 py-16 text-center">
        <img
          className="h-20 mx-auto mb-8"
          src="https://res.cloudinary.com/dti7egpsg/image/upload/v1705671150/SIT%20Align/sit_app_logo_dsr3ee.png"
          alt="SIT HV Lab Logo"
        />
        
        <h1 className="font-heading text-4xl font-bold text-gray-900 mb-4 sm:text-5xl">
          Virtual High Voltage Laboratory
        </h1>
        
        <p className="font-sans text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
          A web-based platform to enhance teaching and learning of topics related to high voltage engineering.
        </p>
        
        <div className="mb-8">
          <LoginButton />
        </div>

        <div className="mb-8">
          <Link
            to="/staff"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            Staff / Admin (Active Directory) Sign In
          </Link>
          {!isAadConfigured ? (
            <p className="mt-2 text-xs text-gray-500">Staff sign-in is not configured for this environment.</p>
          ) : null}
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-2">
            Need help accessing the lab?
          </p>
          <a 
            href="mailto:support@plexflo.com" 
            className="inline-flex items-center text-sm font-semibold text-blue-600 hover:text-blue-700"
          >
            Contact Support
            <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </a>
        </div>
        
        <div className="mt-12">
          <img
            className="rounded-lg shadow-xl mx-auto max-w-2xl"
            src="https://res.cloudinary.com/dti7egpsg/image/upload/v1699327107/SIT%20Align/landingPage_image_ebem1q.png"
            alt="Virtual Lab Preview"
          />
        </div>
      </div>
    </div>
  )
}
