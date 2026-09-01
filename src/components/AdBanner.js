import { XCircleIcon, XMarkIcon } from '@heroicons/react/20/solid'
import { Button } from "flowbite-react"

export default function AdBanner() {
  return (
    <div className="relative isolate flex items-center gap-x-6 overflow-hidden bg-gray-50 px-6 py-2.5 sm:px-3.5 sm:before:flex-1 font-sans">
      <div
        className="absolute left-[max(-7rem,calc(50%-52rem))] top-1/2 -z-10 -translate-y-1/2 transform-gpu blur-2xl"
        aria-hidden="true"
      >
        <div
          className="aspect-[577/310] w-[36.0625rem] bg-gradient-to-r from-[#ff80b5] to-[#9089fc] opacity-30"
          style={{
            clipPath:
              'polygon(74.8% 41.9%, 97.2% 73.2%, 100% 34.9%, 92.5% 0.4%, 87.5% 0%, 75% 28.6%, 58.5% 54.6%, 50.1% 56.8%, 46.9% 44%, 48.3% 17.4%, 24.7% 53.9%, 0% 27.9%, 11.9% 74.2%, 24.9% 54.1%, 68.6% 100%, 74.8% 41.9%)',
          }}
        />
      </div>
      <div
        className="absolute left-[max(45rem,calc(50%+8rem))] top-1/2 -z-10 -translate-y-1/2 transform-gpu blur-2xl"
        aria-hidden="true"
      >
        <div
          className="aspect-[577/310] w-[36.0625rem] bg-gradient-to-r from-[#ff80b5] to-[#9089fc] opacity-30"
          style={{
            clipPath:
              'polygon(74.8% 41.9%, 97.2% 73.2%, 100% 34.9%, 92.5% 0.4%, 87.5% 0%, 75% 28.6%, 58.5% 54.6%, 50.1% 56.8%, 46.9% 44%, 48.3% 17.4%, 24.7% 53.9%, 0% 27.9%, 11.9% 74.2%, 24.9% 54.1%, 68.6% 100%, 74.8% 41.9%)',
          }}
        />
      </div>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <p className="text-sm leading-6 text-gray-900">
          <strong className="font-semibold">App Now Integrated with Brightspace LTI and SIT ADFS . Updated on March 20, 2026</strong>
          <svg viewBox="0 0 2 2" className="mx-2 inline h-0.5 w-0.5 fill-current" aria-hidden="true">
            <circle cx={1} cy={1} r={1} />
          </svg>
          Report issues to the development team.
        </p>
        <Button outline gradientDuoTone="redToYellow" className="out" size="sm" rounded="md" onClick={() => window.open("https://docs.google.com/forms/d/e/1FAIpQLSc5tkZWMMambRuszuSJ4qc5iv3iHCCUeu4Afn_LJ-mRSJsHhw/viewform?usp=sharing")}>
                    Report Issues
        </Button>
      </div>
      <div className="flex flex-1 justify-end">
        <button type="button" className="-m-3 p-3 focus-visible:outline-offset-[-4px]">
          <span className="sr-only">Dismiss</span>
          {/* <XMarkIcon className="h-5 w-5 text-gray-900" aria-hidden="true" /> */}
        </button>
      </div>
    </div>

    // <div className="rounded-md bg-red-50 p-4 font-sans">
    //   <div className="flex">
    //     <div className="flex-shrink-0">
    //       <XCircleIcon className="h-5 w-5 text-red-400" aria-hidden="true" />
    //     </div>
    //     <div className="ml-3 max-w-7xl items-center">
    //       <h3 className="text-sm font-medium text-red-800">There are 2 active errors</h3>
    //       <div className="mt-2 text-sm text-red-700">
    //         <ul role="list" className="list-disc space-y-1 pl-5">
    //           <li>Cannot ping or reach Grid Edge Controller/Device Master Node</li>
    //           <li>No data received on pub/sub channels</li>
    //         </ul>
    //       </div>
    //     </div>
    //   </div>
    // </div>
  )
}
